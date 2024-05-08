const Configuration = {
    extends: ['@commitlint/config-conventional'],
    rules: {
       // Increase to 300 characters for max line length in body
    "body-max-line-length": [2, "always", 300],
    // Increase to 300 characters for max line length in footer
    "footer-max-line-length": [2, "always", 300],
    },
  };

  export default Configuration;
