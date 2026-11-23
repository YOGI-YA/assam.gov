'use client';

import { AppLayout } from '@/components/layout/AppLayout';
import { DraftingStudio } from '@/components/drafting/DraftingStudio';

export default function DraftingPage() {
  return (
    <AppLayout currentModule="Drafting Studio">
      <DraftingStudio />
    </AppLayout>
  );
}
