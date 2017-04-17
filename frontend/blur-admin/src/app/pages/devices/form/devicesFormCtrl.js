(function () {
  'use strict';

  angular.module('BlurAdmin.pages.devices.form')
    .controller('DevicesFormCtrl', DevicesFormCtrl)

  /** @ngInject */
  function DevicesFormCtrl($scope, baProgressModal, $http, $timeout, $location) {

    var vm = this;

    vm.deviceInfo = {};
    vm.locationsForm = {};
    vm.deviceProfilesForm = {};

    vm.locationModels = [];
    $http({
      method: 'GET',
      url: '/api/v1.0/locations/'
    }).then(function successCallback(response) {
        console.log(response)
        vm.locationModels["models"] = response.data.data;
      }, function errorCallback(response) {
        console.log(response)
      }
    );

    vm.deviceTypeSelectItems = [
      {label: 'Juniper SRX', value: 'juniper_srx'},
      {label: 'Palo Alto Panorama', value: 'palo_alto_panorama'},
    ];

    vm.deviceProfileInstances = [""];
    vm.addNewDeviceProfile = function(){
      var instance = "";
      vm.deviceProfileInstances.splice(vm.deviceProfileInstances.length,0,instance);
      console.log(vm.deviceProfileInstances);
    };

    vm.removeDeviceProfile = function($event,index){
      if($event.which == 1){
        vm.deviceProfileInstances.splice(index, 1);
      }
    };

    vm.mappingInstances = []
    vm.addNewZoneMapping = function(){
      var instance = {profile: "", zoneMapping: {zoneName:"", network:""}};
      vm.mappingInstances.splice(vm.mappingInstances.length,0,instance);
    };

    vm.removeZoneMapping = function($event,index){
      if($event.which == 1){
        vm.mappingInstances.splice(index, 1);
      }
    };

    vm.mappingRulesInstances = []
    vm.addNewZoneMappingRule = function(){
      var instance = {profile: "", zoneMappingRule: {sourceZoneName:"", destinationNetwork:"", destinationZoneName:""}};
      vm.mappingRulesInstances.splice(vm.mappingRulesInstances.length,0,instance);
    };

    vm.removeZoneMappingRule = function($event,index){
      if($event.which == 1){
        vm.mappingRulesInstances.splice(index, 1);
      }
    };

    vm.locations = []
    vm.addNewLocation = function(){
      var instance = {profile:"", location: {name:"", id:""}};
      vm.locations.splice(vm.locations.length,0,instance);
    };

    vm.removeLocation = function($event,index){
      if($event.which == 1){
        vm.locations.splice(index, 1);
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

      var profiles = [];
      vm.deviceProfileInstances.forEach(function(element) {

        var profileFilter = function(p){
          return p.profile === element;
        }
        
        var profile_instance = {name: element, zone_mappings: [], zone_mapping_rules: [], locations: []};

        var zone_maps = vm.mappingInstances.filter(profileFilter);
        zone_maps.forEach(function(e) {
          profile_instance.zone_mappings.push({
            zone_name: e.zoneMapping.zoneName, 
            network: e.zoneMapping.network
          })
        }, this);

        var zone_map_rules = vm.mappingRulesInstances.filter(profileFilter);
        zone_map_rules.forEach(function(e) {
          profile_instance.zone_mapping_rules.push({
            source_zone_name: e.zoneMappingRule.sourceZoneName, 
            destination_network: e.zoneMappingRule.destinationNetwork,
            destination_zone_name: e.zoneMappingRule.destinationZoneName
          })
        }, this);

        var locations = vm.locations.filter(profileFilter);
        locations.forEach(function(e) {
          profile_instance.locations.push(e.location.id);
        }, this);

        profiles.push(profile_instance)

      }, this);

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
          device_profiles: profiles
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