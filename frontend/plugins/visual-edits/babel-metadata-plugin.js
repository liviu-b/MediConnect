/**
 * Babel Metadata Plugin
 * Adds metadata to JSX elements for visual editing tools
 */

module.exports = function babelMetadataPlugin({ types: t }) {
  return {
    name: 'babel-metadata-plugin',
    visitor: {
      JSXElement(path, state) {
        // Skip if already has metadata
        const openingElement = path.node.openingElement;
        const hasMetadata = openingElement.attributes.some(
          attr => t.isJSXAttribute(attr) && attr.name.name === 'data-component-path'
        );

        if (hasMetadata) {
          return;
        }

        // Add metadata attribute with file location
        const filename = state.file.opts.filename;
        const { line, column } = path.node.loc.start;

        const metadataAttr = t.jsxAttribute(
          t.jsxIdentifier('data-component-path'),
          t.stringLiteral(`${filename}:${line}:${column}`)
        );

        openingElement.attributes.push(metadataAttr);
      },
    },
  };
};
