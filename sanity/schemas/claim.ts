export default {
  name: 'claim',
  title: 'Claim',
  type: 'document',
  fields: [
    { name: 'session', type: 'reference', to: [{ type: 'session' }], title: 'Session' },
    { name: 'topic', type: 'reference', to: [{ type: 'topic' }], title: 'Topic' },
    { name: 'text', type: 'text', title: 'Text' },
    { name: 'stance', type: 'string', options: { list: ['support', 'oppose', 'neutral'] }, title: 'Stance' },
    { name: 'sources', type: 'array', of: [{ type: 'reference', to: [{ type: 'source' }] }], title: 'Sources' },
  ],
};
