export default {
  name: 'source',
  title: 'Source',
  type: 'document',
  fields: [
    { name: 'url', type: 'url', title: 'URL' },
    { name: 'title', type: 'string', title: 'Title' },
    { name: 'snippet', type: 'text', title: 'Snippet' },
    { name: 'sourceName', type: 'string', title: 'Source Name' },
  ],
};
