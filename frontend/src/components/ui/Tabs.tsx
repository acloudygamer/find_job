import { useState } from 'react';
import type { ReactNode } from 'react';

interface Tab {
  id: string;
  label: string;
  content: ReactNode;
}

interface TabsProps {
  tabs: Tab[];
  defaultTab?: string;
}

export function Tabs({ tabs, defaultTab }: TabsProps) {
  const [active, setActive] = useState<string>(
    defaultTab ?? tabs[0]?.id ?? ''
  );

  return (
    <div>
      {/* Tab list */}
      <div className="flex border-b border-gray-200 gap-1">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActive(tab.id)}
            className={[
              'px-4 py-2 text-sm font-medium transition-colors',
              'border-b-2 -mb-px',
              active === tab.id
                ? 'border-primary-500 text-primary-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300',
            ].join(' ')}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab content */}
      <div className="py-4">{tabs.find((t) => t.id === active)?.content}</div>
    </div>
  );
}
