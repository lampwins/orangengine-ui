(function () {
  'use strict';

  angular.module('BlurAdmin.pages.devices.form')
    .controller('DevicesFormCtrl', DevicesFormCtrl)

  /** @ngInject */
  function DevicesFormCtrl($scope, baProgressModal, $http, $timeout, $location) {

    var vm = this;

    vm.deviceInfo = {};

    vm.deviceTypeSelectItems = [
      {label: 'Juniper SRX', value: 'juniper_srx'},
      {label: 'Palo Alto Panorama', value: 'palo_alto_panorama'},
    ];

    vm.mappingInstances = []
    vm.addNewZoneMapping = function(){
      var instance = {zoneName:"", network:""};
      vm.mappingInstances.splice(vm.mappingInstances.length,0,instance);
    };

    vm.removeZoneMapping = function($event,index){
      if($event.which == 1){
        vm.mappingInstances.splice(index, 1);
      }
    };

    vm.mappingRulesInstances = []
    vm.addNewZoneMappingRule = function(){
      var instance = {sourceZoneName:"", destinationNetwork:"", destinationZoneName:""};
      vm.mappingRulesInstances.splice(vm.mappingRulesInstances.length,0,instance);
    };

    vm.removeZoneMappingRule = function($event,index){
      if($event.which == 1){
        vm.mappingRulesInstances.splice(index, 1);
      }
    };

    vm.validIpAddressRegex = "^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$";
    vm.validIpNetworkRegex = "^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])(\/([0-9]|[1-2][0-9]|3[0-2]))$";
    vm.valid952HostnameRegex = "^(([a-zA-Z]|[a-zA-Z][a-zA-Z0-9\-]*[a-zA-Z0-9])\.)*([A-Za-z]|[A-Za-z][A-Za-z0-9\-]*[A-Za-z0-9])$";
    vm.validIpOr952Hostname = "^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])|(([a-zA-Z]|[a-zA-Z][a-zA-Z0-9\-]*[a-zA-Z0-9])\.)*([A-Za-z]|[A-Za-z][A-Za-z0-9\-]*[A-Za-z0-9])$"

    vm.submitForm = function(){
      // open the progress modal
      baProgressModal.open();
      baProgressModal.setProgress(50);  // hehe

      var zone_mappings = [];
      vm.mappingInstances.forEach(function(element) {
        zone_mappings.push({
          zone_name: element.zoneName, 
          network: element.network
        });
      }, this);

      var zone_mapping_rules = [];
      vm.mappingRulesInstances.forEach(function(element) {
        zone_mapping_rules.push({
          source_zone_name: element.sourceZoneName, 
          destination_network: element.destinationNetwork,
          destination_zone_name: element.destinationZoneName
        });
      }, this);

      var supplemental_device_params = [];
      if (vm.deviceInfo.deviceTypeItem.value == 'palo_alto_panorama') {
        supplemental_device_params.push({
          device_group: vm.deviceInfo.panoramaDevGroup
        })
      }

      $http({
        method: 'PUT',
        url: '/api/v1.0/devices/',
        data: {
          common_name: vm.deviceInfo.common_name,
          hostname: vm.deviceInfo.hostname,
          username: vm.deviceInfo.username,
          driver: vm.deviceInfo.deviceTypeItem.value,
          password: vm.deviceInfo.password || null,
          apikey: vm.deviceInfo.apikey || null,
          zone_mappings: zone_mappings,
          zone_mapping_rules: zone_mapping_rules,
          supplemental_device_params: supplemental_device_params
        }
      }).then(function successCallback(response) {
          baProgressModal.setProgress(100);
          $timeout($location.path('/devices/list'), 2000);
          $timeout( baProgressModal.close(), 2000);
        }, function errorCallback(response) {
          baProgressModal.close();
          console.error("Failed to PUT device.")
          console.error(response)
        }
      );

    };

  };

})();