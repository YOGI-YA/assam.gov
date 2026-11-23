'use client';

import { AppLayout } from '@/components/layout/AppLayout';
import { AskGovSaarthi } from '@/components/chat/AskGovSaarthi';

export default function HomePage() {
  return (
    <AppLayout>
      <AskGovSaarthi />
    </AppLayout>
  );
}
