const Incentive = artifacts.require("Incentive");

module.exports = function (deployer) {
  deployer.deploy(Incentive);
};
