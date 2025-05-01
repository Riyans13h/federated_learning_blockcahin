module.exports = {
  networks: {
    development: {
      host: "127.0.0.1",     // Localhost (default: none)
      port: 7545,            // Ganache GUI port
      network_id: "*"        // Match any network id
    },
    develop: {
      port: 8545             // Ganache CLI port
    }
  },

  // Add compiler settings here 👇
  compilers: {
    solc: {
      version: "0.8.20",     // ✅ Replace with the version your contract needs
      settings: {
        optimizer: {
          enabled: true,
          runs: 200
        },
        evmVersion: "istanbul"
      }
    }
  }
};
