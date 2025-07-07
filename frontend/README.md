# API Sentinel Frontend

This is the frontend application for API Sentinel, built with Next.js, Tailwind CSS, and ShadCN UI.

## Features

- Modern dashboard with clean UX
- Project overview with traffic graphs and alerts
- Endpoint explorer
- Anomalies timeline
- API documentation viewer
- Settings management

## Getting Started

### Prerequisites

- Node.js 18.x or later
- npm or yarn

### Installation

1. Install dependencies:

```bash
npm install
# or
yarn install
```

2. Create a `.env.local` file with the following variables:

```
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_URL=http://localhost:3000
CLERK_PUBLISHABLE_KEY=your_clerk_publishable_key
CLERK_SECRET_KEY=your_clerk_secret_key
```

3. Run the development server:

```bash
npm run dev
# or
yarn dev
```

4. Open [http://localhost:3000](http://localhost:3000) in your browser.

## Project Structure

- `app/` - Next.js App Router pages and layouts
- `components/` - React components
- `lib/` - Utility functions and hooks
- `public/` - Static assets
- `styles/` - Global styles

## Deployment

The frontend is designed to be deployed on Vercel:

```bash
vercel
```

## License

MIT