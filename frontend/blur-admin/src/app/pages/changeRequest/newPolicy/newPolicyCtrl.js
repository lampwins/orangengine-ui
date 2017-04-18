(function () {
  'use strict';

  angular.module('BlurAdmin.pages.changeRequest.newPolicy')
      .controller('NewPolicyCtrl', NewPolicyCtrl);

  /** @ngInject */
  function NewPolicyCtrl($scope) {

    var vm = this;

        vm.personalInfo = {};
        vm.productInfo = {};
        vm.shipment = {};

        vm.arePersonalInfoPasswordsEqual = function () {
          return vm.personalInfo.confirmPassword && vm.personalInfo.password == vm.personalInfo.confirmPassword;
        };


  }
})();
