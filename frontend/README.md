# Frontend Setup Guide

## Prerequisites

- Node.js 18+ or higher
- npm, yarn, or pnpm (package manager)
- Git

## Installation Steps

### 1. Install Dependencies

```bash
cd frontend
npm install
# or
yarn install
# or
pnpm install
```

### 2. Environment Configuration

```bash
cp .env.example .env.local
```

Edit `.env.local` with your configuration:
- `VITE_SUPABASE_URL`: Your Supabase project URL
- `VITE_SUPABASE_ANON_KEY`: Your Supabase anon key
- `VITE_API_URL`: Backend API URL (http://localhost:8000 for development)

### 3. Run Development Server

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
```

Application will be available at: `http://localhost:5173`

## Available Scripts

### Development
```bash
npm run dev      # Start dev server with hot reload
npm run type-check  # Check TypeScript types
npm run lint     # Run ESLint
```

### Production
```bash
npm run build    # Build for production
npm run preview  # Preview production build locally
```

## Project Structure

```
frontend/
├── src/
│   ├── components/       # Reusable UI components
│   ├── hooks/            # Custom React hooks
│   ├── pages/            # Page components
│   ├── services/         # API & Supabase clients
│   ├── types/            # TypeScript type definitions
│   ├── utils/            # Utility functions
│   ├── styles/           # CSS and Tailwind
│   ├── App.tsx           # Root component
│   └── main.tsx          # Entry point
├── public/               # Static assets
├── package.json          # Dependencies
├── tsconfig.json         # TypeScript config
├── vite.config.ts        # Vite config
├── tailwind.config.ts    # Tailwind CSS config
└── README.md             # This file
```

## Styling with Tailwind CSS

This project uses Tailwind CSS for styling. All CSS is utility-first.

```jsx
// Example component with Tailwind
export function Button() {
  return (
    <button className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition">
      Click me
    </button>
  );
}
```

## TypeScript Strict Mode

TypeScript is configured in strict mode to catch errors at compile time:
- `strict: true` - Enables all strict type-checking options
- `noImplicitAny: true` - Error on implicit `any` types
- `strictNullChecks: true` - Strict null checking

Always add explicit types to your code:

```tsx
// ✅ Good
interface User {
  id: string;
  email: string;
}

const user: User = { id: "1", email: "test@example.com" };

// ❌ Bad
const user = { id: "1", email: "test@example.com" };
```

## State Management

This project uses **Zustand** for state management:

```tsx
import { create } from 'zustand';

interface Store {
  user: User | null;
  setUser: (user: User) => void;
}

const useStore = create<Store>((set) => ({
  user: null,
  setUser: (user) => set({ user }),
}));

// Usage in component
function MyComponent() {
  const { user, setUser } = useStore();
  // ...
}
```

## API Integration

All API calls should go through typed service files in `src/services/`:

```typescript
// src/services/api.ts
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL;

export const api = axios.create({
  baseURL: API_URL,
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('authToken');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
```

## Authentication Flow

Authentication is handled via Supabase Auth:

```typescript
import { useAuth } from '@/hooks/useAuth';

function LoginPage() {
  const { login, user } = useAuth();
  
  const handleLogin = async (email: string, password: string) => {
    const { user, error } = await login(email, password);
    if (error) {
      console.error('Login failed:', error);
    }
  };
  
  return (
    // JSX here
  );
}
```

## Routing

Frontend uses React Router for navigation:

```tsx
import { BrowserRouter, Routes, Route } from 'react-router-dom';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/login" element={<Login />} />
      </Routes>
    </BrowserRouter>
  );
}
```

## Dark Mode

Tailwind CSS dark mode is enabled. Use `dark:` prefix for dark mode styles:

```jsx
<div className="bg-white dark:bg-gray-900 text-black dark:text-white">
  Content that adapts to dark mode
</div>
```

## Performance Tips

1. **Code Splitting**: Use React.lazy() for route-based code splitting
2. **Images**: Use modern formats (WebP) and optimize sizes
3. **Bundle**: Check bundle size with `npm run build`
4. **Caching**: Leverage HTTP caching headers
5. **Lazy Loading**: Lazy load components and images

## Accessibility

- Use semantic HTML (`<button>`, `<nav>`, `<article>`)
- Include alt text for images
- Ensure color contrast meets WCAG standards
- Use ARIA attributes when needed
- Test with keyboard navigation

## Testing

```bash
# Tests will be added in Phase 5
npm test -- --coverage
```

## Troubleshooting

### Port 5173 already in use
```bash
npm run dev -- --port 3000
```

### Environment variables not loading
- Restart dev server after changing `.env.local`
- Prefix variables with `VITE_`

### Tailwind styles not applying
- Check that `tailwind.config.ts` includes `src/**/*.{js,ts,jsx,tsx}`
- Restart dev server
- Clear Vite cache: `rm -rf node_modules/.vite`

## Next Steps

1. Run the dev server: `npm run dev`
2. Check that it loads at `http://localhost:5173`
3. Verify Supabase connection works
4. Wait for Phase 2 to implement authentication UI
