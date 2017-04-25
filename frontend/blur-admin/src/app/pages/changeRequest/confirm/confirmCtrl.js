(function () {
  'use strict';

  angular.module('BlurAdmin.pages.changeRequest.confirm')
      .controller('ConfirmCtrl', ConfirmCtrl);

  /** @ngInject */
  function ConfirmCtrl($scope, candidatePolicyService, $location, $http) {

    var candidate_policy = candidatePolicyService.retrieveCandiatePolicy();
    if (candidate_policy === undefined) {
      $location.path('/dashboard');
    }

    var device = candidatePolicyService.getDevice();
    var profile = candidatePolicyService.getProfile();

    var methodMap = {
      NEW_POLICY: 'New Policy',
      TAG: 'Tag Object(s)',
      APPEND: 'Append to Existing Policy'
    }

    var vm = this;

    vm.device = device;
    vm.profile = profile;
    vm.candidate_policy = candidate_policy;
    vm.method = methodMap[vm.candidate_policy.method];

    vm.commitFormData = {
      commit: false
    };

    vm.submitForm = function() {
      $http({
        method : "POST",
        url : "/api/v1.0/oe/apply_candidate_policy/",
        data: {
          device: {
            hostname: vm.device.hostname
          },
          candidate_policy: candidate_policy,
          commit: vm.commitFormData.commit
        }
      }).then(function mySuccess(response){
        console.log(response);
      }, function myError(response) {
        console.log(response)
      });
    }

  }
})();
