/** Optional: for explicit support/oppose relationships between claims (contradictions). */
export default {
  name: 'claimEdge',
  title: 'Claim Edge',
  type: 'document',
  fields: [
    { name: 'fromClaim', type: 'reference', to: [{ type: 'claim' }], title: 'From Claim' },
    { name: 'toClaim', type: 'reference', to: [{ type: 'claim' }], title: 'To Claim' },
    { name: 'relation', type: 'string', options: { list: ['supports', 'opposes'] }, title: 'Relation' },
  ],
};
