(function () {
  'use strict';

  angular.module('BlurAdmin.pages.changeRequest.summary')
      .controller('SummaryCtrl', SummaryCtrl);

  /** @ngInject */
  function SummaryCtrl($scope, $location, $stateParams, changeRequestService, candidatePolicyService, $http, $uibModal, $uibModalStack) {

    var vm = this;
    vm.change_request = null;
    vm.automation_score = null;
    vm.environmentForm = {};
    vm.candidate_policy = null;
    vm.candidatePolicyMethodMap = {
      NEW_POLICY: 'New Policy',
      TAG: 'Tag',
      APPEND: 'Append',
      'New Policy': 'NEW_POLICY',
      'Tag': 'TAG',
      'Append': 'APPEND'
    }
    vm.environmentForm.allMethods = [
      'New Policy',
      'Tag',
      'Append'
    ]

    changeRequestService.updateId($stateParams.id);

    changeRequestService.getChangeRequest().then(function(data){
      vm.change_request = data;
    });

    changeRequestService.getScore($stateParams.id).then(function(data){
      vm.automation_score = data;
      vm.environmentForm.device = vm.automation_score.environment[0].device;
      vm.environmentForm.deviceProfile = vm.automation_score.environment[0].profile;
      vm.updateCandidatePolicy();
    });

    $http({
      method : "GET",
      url : "/api/v1.0/devices/"
    }).then(function mySuccess(response){
      console.log(response);
      vm.environmentForm.allDevices = response.data.data;
    }, function myError(response) {
      console.log(response)
    });

    vm.updateCandidatePolicy = function() {
      if (vm.environmentForm.device !== undefined && vm.environmentForm.deviceProfile !== undefined) {
        matchCriteria = matchCriteria(vm.environmentForm.device);
        candidatePolicyService.getCandidatePolicy(vm.environmentForm.device, vm.environmentForm.deviceProfile, matchCriteria).then(function(data){
          vm.candidate_policy = data;
          vm.environmentForm.method = vm.candidatePolicyMethodMap[vm.candidate_policy.method];
        });
      }
    };

    function matchCriteria(device) {
      var data = {};
      var envPos = vm.automation_score.environment.map(function(x) {return x.device; }).indexOf(device);
      var envObject = vm.automation_score.environment[envPos];

      data.source_zones = envObject.zones.source;
      data.destination_zones = envObject.zones.destination;
      data.source_addresses = vm.change_request.sources.map(function(x) {return x.value;});
      data.destination_addresses = vm.change_request.destinations.map(function(x) {return x.value;});
      data.services = vm.change_request.services.filter(function(x) {return x.type==='layer4';}).map(function(x) {return [x.layer4_protocol, x.layer4_port];});
      if (device.driver === 'palo_alto_panorama'){
        data.applications = vm.change_request.services.filter(function(x) {return x.type==='layer7';}).map(function(x) {return x.layer7_value;});
      }
      data.action = vm.change_request.action;

      return data;
    }


    vm.cancel = function() {
      $scope.changeRequestCancelId = vm.change_request.id;
      $uibModal.open({
        animation: true,
        templateUrl: 'app/pages/changeRequest/summary/manualCloseConfirmModal.html',
        size: 'sm',
        scope: $scope
      });
    }

    vm.cancelConfirm = function(id) {
      console.log(id);
      $http({
        method : "PATCH",
        url : "/api/v1.0/change_requests/" + id + "/",
        data: {
          status: "manually_closed"
        }
      }).then(function mySuccess(response){
        console.log(response)
        $uibModalStack.dismissAll();
        $location.path('/dashboard');
        console.log(vm.queueData);
      }, function myError(response) {
        console.log(response)
      });
    }

    vm.proceed = function(){
      if (vm.environmentForm.device !== undefined && vm.environmentForm.deviceProfile != undefined && vm.environmentForm.method !== undefined) {
        
        candidatePolicyService.updateDevice(vm.environmentForm.device);
        candidatePolicyService.updateProfile(vm.environmentForm.deviceProfile);
        var candidate_policy = vm.candidate_policy;
        candidate_policy.method = vm.candidatePolicyMethodMap[vm.environmentForm.method];
        candidatePolicyService.updateCandidatePolicy(candidate_policy);
        console.log(candidate_policy.method);
        
        switch(candidate_policy.method){
          case 'NEW_POLICY': $location.path('/changeRequest/' + vm.change_request.id + '/newPolicy');
            break;
          case 'APPEND': $location.path('/changeRequest/' + vm.change_request.id + '/append');
            break;
          case 'TAG': $location.path('/changeRequest/' + vm.change_request.id + '/tag');
            break;
        }
      
    }
    }

  }
})();
