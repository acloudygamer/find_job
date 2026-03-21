import type { ReactNode } from 'react';

interface CardProps {
  children: ReactNode;
  className?: string;
  onClick?: () => void;
  hoverable?: boolean;
}

export function Card({
  children,
  className = '',
  onClick,
  hoverable = false,
}: CardProps) {
  return (
    <div
      onClick={onClick}
      className={[
        'bg-white rounded-xl border border-gray-200 shadow-sm',
        hoverable &&
          'hover:shadow-md hover:border-primary-200 cursor-pointer transition-all duration-150',
        onClick && 'cursor-pointer',
        className,
      ]
        .filter(Boolean)
        .join(' ')}
    >
      {children}
    </div>
  );
}

export function CardHeader({
  children,
  className = '',
}: {
  children: ReactNode;
  className?: string;
}) {
  return (
    <div className={['px-5 py-4 border-b border-gray-100', className].join(' ')}>
      {children}
    </div>
  );
}

export function CardBody({
  children,
  className = '',
}: {
  children: ReactNode;
  className?: string;
}) {
  return <div className={['px-5 py-4', className].join(' ')}>{children}</div>;
}

export function CardFooter({
  children,
  className = '',
}: {
  children: ReactNode;
  className?: string;
}) {
  return (
    <div
      className={['px-5 py-3 border-t border-gray-100 bg-gray-50 rounded-b-xl', className].join(' ')}
    >
      {children}
    </div>
  );
}
