import React from 'react';
import { redirect } from 'next/navigation';

export default function Home() {
  // Redirect to landing page by default
  redirect('/landing');
}
