'use client';

import { AppLayout } from '@/components/layout/AppLayout';
import { AskGovSaarthi } from '@/components/chat/AskGovSaarthi';

export default function ChatPage() {
  return (
    <AppLayout currentModule="Ask GovSaarthi">
      <AskGovSaarthi />
    </AppLayout>
  );
}
