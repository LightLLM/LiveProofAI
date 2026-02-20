export default {
  name: 'session',
  title: 'Session',
  type: 'document',
  fields: [
    { name: 'topic', type: 'reference', to: [{ type: 'topic' }], title: 'Topic' },
    { name: 'question', type: 'string', title: 'Question' },
    { name: 'answer', type: 'text', title: 'Answer' },
    { name: 'reliabilityScore', type: 'number', title: 'Reliability Score' },
    { name: 'canExecute', type: 'boolean', title: 'Can Execute' },
    { name: 'claims', type: 'array', of: [{ type: 'reference', to: [{ type: 'claim' }] }], title: 'Claims' },
    { name: 'createdAt', type: 'datetime', title: 'Created At' },
  ],
};
