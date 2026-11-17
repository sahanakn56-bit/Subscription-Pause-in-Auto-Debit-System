# Frontend - Subscription Pause in Auto-Debit System

React application built with [Vite](https://vite.dev/) for the Subscription Pause in Auto-Debit System UI.

## Getting Started

### 1. Navigate to the Frontend directory
```powershell
cd Frontend
```

### 2. Run the Development Server
```powershell
npm run dev
```

> **Note for Windows PowerShell:** If running `npm` produces a script execution policy error (`npm.ps1 cannot be loaded`), use `npm.cmd`:
> ```powershell
> npm.cmd run dev
> ```
> Or temporarily enable script execution in your session:
> ```powershell
> Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
> ```

The application will be running at [http://localhost:5173](http://localhost:5173).

### 3. Backend Integration
The Vite dev server is pre-configured in [vite.config.js](vite.config.js) to proxy `/api` requests to the FastAPI backend running at `http://127.0.0.1:8000`.

### 4. Build for Production
```powershell
npm run build
```
The compiled output is saved to the `dist/` directory.
