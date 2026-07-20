-- Axiom AI Database Schema
-- PostgreSQL Database for Axiom AI Learning Platform

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table (managed by Supabase Auth, but we add additional fields)
CREATE TABLE IF NOT EXISTS users (
  id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  email VARCHAR(255) NOT NULL UNIQUE,
  full_name VARCHAR(255),
  avatar_url TEXT,
  role VARCHAR(50) DEFAULT 'student', -- student, teacher, admin
  bio TEXT,
  preferences JSONB DEFAULT '{"theme": "light", "notifications": true}'::jsonb,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT valid_role CHECK (role IN ('student', 'teacher', 'admin'))
);

-- Notes table (uploaded notes by students)
CREATE TABLE IF NOT EXISTS notes (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  title VARCHAR(255) NOT NULL,
  description TEXT,
  file_path TEXT NOT NULL, -- Path in Supabase Storage
  file_size_bytes INTEGER NOT NULL,
  file_type VARCHAR(50) NOT NULL, -- pdf, png, jpg, jpeg
  extracted_text TEXT, -- Raw text extracted from the note
  raw_content JSONB, -- Structured content from the note
  status VARCHAR(50) DEFAULT 'processing', -- processing, completed, failed
  processing_error TEXT, -- Error message if processing fails
  is_public BOOLEAN DEFAULT false,
  tags JSONB DEFAULT '[]'::jsonb, -- Array of topic tags
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT valid_file_type CHECK (file_type IN ('pdf', 'png', 'jpg', 'jpeg'))
);

-- Topics table (derived from student notes)
CREATE TABLE IF NOT EXISTS topics (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  note_id UUID NOT NULL REFERENCES notes(id) ON DELETE CASCADE,
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  title VARCHAR(255) NOT NULL,
  description TEXT,
  content TEXT, -- Extracted topic content from the note
  embeddings VECTOR(1536), -- Vector embeddings for semantic search (if using pgvector)
  subtopics JSONB DEFAULT '[]'::jsonb, -- Array of subtopic titles
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Quiz Sessions table
CREATE TABLE IF NOT EXISTS quiz_sessions (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  note_id UUID NOT NULL REFERENCES notes(id) ON DELETE CASCADE,
  topic_id UUID REFERENCES topics(id) ON DELETE SET NULL,
  title VARCHAR(255) NOT NULL,
  status VARCHAR(50) DEFAULT 'in_progress', -- in_progress, completed
  total_questions INTEGER NOT NULL,
  correct_answers INTEGER DEFAULT 0,
  score_percentage DECIMAL(5, 2),
  started_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  completed_at TIMESTAMP WITH TIME ZONE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Quiz Questions table
CREATE TABLE IF NOT EXISTS quiz_questions (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  quiz_session_id UUID NOT NULL REFERENCES quiz_sessions(id) ON DELETE CASCADE,
  note_id UUID NOT NULL REFERENCES notes(id) ON DELETE CASCADE,
  question_text TEXT NOT NULL,
  question_type VARCHAR(50) NOT NULL, -- mcq, short_answer
  context_reference TEXT, -- Reference to the note content
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT valid_question_type CHECK (question_type IN ('mcq', 'short_answer'))
);

-- MCQ Options table
CREATE TABLE IF NOT EXISTS mcq_options (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  question_id UUID NOT NULL REFERENCES quiz_questions(id) ON DELETE CASCADE,
  option_text TEXT NOT NULL,
  is_correct BOOLEAN NOT NULL,
  display_order INTEGER NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Quiz Answers table
CREATE TABLE IF NOT EXISTS quiz_answers (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  quiz_session_id UUID NOT NULL REFERENCES quiz_sessions(id) ON DELETE CASCADE,
  question_id UUID NOT NULL REFERENCES quiz_questions(id) ON DELETE CASCADE,
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  selected_option_id UUID REFERENCES mcq_options(id) ON DELETE SET NULL, -- For MCQ
  user_answer TEXT, -- For short answer
  is_correct BOOLEAN,
  feedback TEXT, -- AI-generated feedback
  time_spent_seconds INTEGER,
  answered_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Student Progress table
CREATE TABLE IF NOT EXISTS student_progress (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  note_id UUID NOT NULL REFERENCES notes(id) ON DELETE CASCADE,
  topic_id UUID REFERENCES topics(id) ON DELETE SET NULL,
  total_interactions INTEGER DEFAULT 0,
  correct_answers INTEGER DEFAULT 0,
  incorrect_answers INTEGER DEFAULT 0,
  average_score DECIMAL(5, 2),
  last_studied_at TIMESTAMP WITH TIME ZONE,
  mastery_level VARCHAR(50) DEFAULT 'beginner', -- beginner, intermediate, advanced, mastered
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- AI Interactions table (for logging and analytics)
CREATE TABLE IF NOT EXISTS ai_interactions (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  note_id UUID NOT NULL REFERENCES notes(id) ON DELETE CASCADE,
  interaction_type VARCHAR(100), -- explanation, example, quiz_feedback, general_query
  user_query TEXT NOT NULL,
  ai_response TEXT NOT NULL,
  tokens_used INTEGER,
  response_time_ms INTEGER,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Revision Recommendations table
CREATE TABLE IF NOT EXISTS revision_recommendations (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  topic_id UUID NOT NULL REFERENCES topics(id) ON DELETE CASCADE,
  note_id UUID NOT NULL REFERENCES notes(id) ON DELETE CASCADE,
  reason VARCHAR(255), -- low_score, not_recently_studied, weak_area
  priority VARCHAR(50) DEFAULT 'medium', -- low, medium, high
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  expires_at TIMESTAMP WITH TIME ZONE,
  CONSTRAINT valid_priority CHECK (priority IN ('low', 'medium', 'high'))
);

-- Create indexes for better query performance
CREATE INDEX idx_notes_user_id ON notes(user_id);
CREATE INDEX idx_notes_status ON notes(status);
CREATE INDEX idx_notes_created_at ON notes(created_at DESC);
CREATE INDEX idx_topics_user_id ON topics(user_id);
CREATE INDEX idx_topics_note_id ON topics(note_id);
CREATE INDEX idx_quiz_sessions_user_id ON quiz_sessions(user_id);
CREATE INDEX idx_quiz_sessions_note_id ON quiz_sessions(note_id);
CREATE INDEX idx_quiz_sessions_status ON quiz_sessions(status);
CREATE INDEX idx_quiz_questions_quiz_session_id ON quiz_questions(quiz_session_id);
CREATE INDEX idx_quiz_answers_quiz_session_id ON quiz_answers(quiz_session_id);
CREATE INDEX idx_quiz_answers_user_id ON quiz_answers(user_id);
CREATE INDEX idx_student_progress_user_id ON student_progress(user_id);
CREATE INDEX idx_student_progress_note_id ON student_progress(note_id);
CREATE INDEX idx_ai_interactions_user_id ON ai_interactions(user_id);
CREATE INDEX idx_revision_recommendations_user_id ON revision_recommendations(user_id);

-- Create views for common queries
-- View: User's recent notes
CREATE OR REPLACE VIEW user_recent_notes AS
SELECT 
  n.id, 
  n.user_id, 
  n.title, 
  n.file_type, 
  n.status, 
  n.created_at,
  COUNT(DISTINCT t.id) as topic_count,
  COUNT(DISTINCT sp.id) as interaction_count
FROM notes n
LEFT JOIN topics t ON n.id = t.note_id
LEFT JOIN student_progress sp ON n.id = sp.note_id
GROUP BY n.id, n.user_id, n.title, n.file_type, n.status, n.created_at
ORDER BY n.created_at DESC;

-- View: Student's overall statistics
CREATE OR REPLACE VIEW student_statistics AS
SELECT 
  u.id as user_id,
  u.email,
  u.full_name,
  COUNT(DISTINCT n.id) as total_notes,
  COUNT(DISTINCT qs.id) as total_quizzes,
  AVG(qs.score_percentage) as average_quiz_score,
  MAX(qs.completed_at) as last_activity
FROM users u
LEFT JOIN notes n ON u.id = n.user_id
LEFT JOIN quiz_sessions qs ON u.id = qs.user_id AND qs.status = 'completed'
GROUP BY u.id, u.email, u.full_name;

-- Enable RLS (Row Level Security) for multi-tenant safety
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE notes ENABLE ROW LEVEL SECURITY;
ALTER TABLE topics ENABLE ROW LEVEL SECURITY;
ALTER TABLE quiz_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE student_progress ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_interactions ENABLE ROW LEVEL SECURITY;

-- RLS Policies
-- Users can only see their own profile
CREATE POLICY users_select_policy ON users
  FOR SELECT USING (auth.uid() = id);

CREATE POLICY users_update_policy ON users
  FOR UPDATE USING (auth.uid() = id);

-- Users can only see their own notes
CREATE POLICY notes_select_policy ON notes
  FOR SELECT USING (auth.uid() = user_id OR is_public = true);

CREATE POLICY notes_insert_policy ON notes
  FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY notes_update_policy ON notes
  FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY notes_delete_policy ON notes
  FOR DELETE USING (auth.uid() = user_id);

-- Similar policies for other tables
CREATE POLICY topics_select_policy ON topics
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY topics_insert_policy ON topics
  FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY quiz_sessions_select_policy ON quiz_sessions
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY quiz_sessions_insert_policy ON quiz_sessions
  FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY student_progress_select_policy ON student_progress
  FOR SELECT USING (auth.uid() = user_id);
