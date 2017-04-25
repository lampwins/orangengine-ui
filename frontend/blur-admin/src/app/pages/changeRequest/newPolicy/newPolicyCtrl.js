(function () {
  'use strict';

  angular.module('BlurAdmin.pages.changeRequest.newPolicy')
      .controller('NewPolicyCtrl', NewPolicyCtrl);

  /** @ngInject */
  function NewPolicyCtrl($scope, candidatePolicyService, $location, $stateParams) {

    var candidate_policy = candidatePolicyService.retrieveCandiatePolicy();
    if (candidate_policy === undefined) {
      $location.path('/dashboard');
    }

    var vm = this;

    var paloAltoAddressTypes = ['ip-netmask', 'ip-range', 'fqdn', 'any'];
    var genericAddressTypes = ['ipv4', 'dns', 'range', 'any'];
    var paloAltoAddressTypeMap = {
      any: 'any',
      ipv4: 'ip-netmask',
      range: 'ip-range',
      dns: 'fqdn'
    };
    var genericAddressTypeMap = {
      any: 'any',
      ipv4: 'ipv4',
      range: 'range',
      dns: 'dns'
    };

    var paloAltoActionTypes = ['allow', 'drop', 'deny'];
    var genericActionTypes = ['Allow', 'Deny', 'Reject', 'Drop'];
    var paloAltoActionTypeMap = {
      allow: 'allow',
      drop: 'drop',
      deny: 'deny'
    };
    var genericActionTypeMap = {
      allow: 'Allow',
      deny: 'Deny',
      reject: 'Reject',
      drop: 'Drop'
    };

    var addressTypeMap, actionTypeMap;
    if (candidatePolicyService.getDevice().driver === 'palo_alto_panorama') {
      addressTypeMap = paloAltoAddressTypeMap;
      vm.addressTypes = paloAltoAddressTypes;
      vm.actionTypes = paloAltoActionTypes;
      actionTypeMap = paloAltoActionTypeMap;
    } else {
      addressTypeMap = genericAddressTypeMap;
      vm.addressTypes = genericAddressTypes;
      vm.actionTypes = genericActionTypes;
      actionTypeMap = genericActionTypeMap;
    }

    function addressType(value) {
      var types = ['IPv4', 'DNS', 'Range', 'Any'];
      if (value === 'any'){
        return addressTypeMap.any;
      } else if (vm.valid952HostnameRegex.test(value)) {
        return addressTypeMap.dns;
      } else if (value.includes('-')) {
        return addressTypeMap.range;
      } else {
        return addressTypeMap.ipv4;
      }
    }

    vm.validIpAddressRegex = /^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$/;
    vm.validIpNetworkRegex = /^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])(\/([0-9]|[1-2][0-9]|3[0-2]))$/;
    vm.valid952HostnameRegex = /^(([a-zA-Z]|[a-zA-Z][a-zA-Z0-9\-]*[a-zA-Z0-9])\.)*([A-Za-z]|[A-Za-z][A-Za-z0-9\-]*[A-Za-z0-9])$/;
    vm.validIpOr952Hostname = /^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])|(([a-zA-Z]|[a-zA-Z][a-zA-Z0-9\-]*[a-zA-Z0-9])\.)*([A-Za-z]|[A-Za-z][A-Za-z0-9\-]*[A-Za-z0-9])$/;


    vm.nameFormData = {};
    vm.sourceFormData = {};
    vm.destinationFormData = {};
    vm.serviceFormData = {};
    vm.actionFormData = {};

    // sources
    vm.sourceFormData.zones = candidate_policy.policy_criteria.source_zones;
    vm.sourceFormData.linked_sources = [];
    vm.sourceFormData.new_sources = [];
    vm.sourceFormData.new_zones = [];
    for (var key in candidate_policy.linked_objects.source_addresses){
      var obj = candidate_policy.linked_objects.source_addresses[key];
      if (obj) {
        // linked
        vm.sourceFormData.linked_sources.push(obj);
      } else {
        // new
        var new_obj = {
          name: null,
          type: addressType(key),
          value: key
        }
        vm.sourceFormData.new_sources.push(new_obj);
      }
    }

    // destinations
    vm.destinationFormData.zones = candidate_policy.policy_criteria.destination_zones;
    vm.destinationFormData.linked_destinations = [];
    vm.destinationFormData.new_destinations = [];
    vm.destinationFormData.new_zones = [];
    for (var key in candidate_policy.linked_objects.destination_addresses){
      var obj = candidate_policy.linked_objects.destination_addresses[key];
      if (obj) {
        // linked
        vm.destinationFormData.linked_destinations.push(obj);
      } else {
        // new
        var new_obj = {
          name: null,
          type: addressType(key),
          value: key
        }
        vm.destinationFormData.new_destinations.push(new_obj);
      }
    }

    // services
    vm.serviceFormData.linked_applications = [];
    vm.serviceFormData.new_applications = [];
    vm.serviceFormData.linked_services = [];
    vm.serviceFormData.new_services = [];
    for (var key in candidate_policy.linked_objects.applications){
      var obj = candidate_policy.linked_objects.applications[key];
      if (obj) {
        // linked
        vm.serviceFormData.linked_applications.push(obj);
      }
    }
    for (var key in candidate_policy.linked_objects.services){
      var obj = candidate_policy.linked_objects.services[key];
      if (obj) {
        // linked
        vm.serviceFormData.linked_services.push(obj);
      } else {
        // new
        var new_obj = {
          name: null,
          protocol: key.split('/')[0],
          port: key.split('/')[1]
        }
        vm.serviceFormData.new_services.push(new_obj);
      }
    }

    // action
    vm.actionFormData.action = actionTypeMap[candidate_policy.policy_criteria.action];

    // submit
    vm.submitForm = function() {

      var policy = {};
      var new_objects = {};
      var linked_objects = {};
      new_objects.source_addresses = {};
      new_objects.destination_addresses = {};
      new_objects.services = {};
      linked_objects.source_addresses = {};
      linked_objects.destination_addresses = {};
      linked_objects.applications = {};
      linked_objects.services = {};
      
      policy.name = vm.nameFormData.name;
      policy.action = vm.actionFormData.action;
      policy.logging = [];
      policy.notes = vm.nameFormData.notes;
      
      policy.source_addresses = [];
      policy.destination_addresses = [];
      policy.applications = [];
      policy.services = [];
      policy.source_zones = [];
      policy.destination_zones = [];

      var linked_sources = vm.sourceFormData.linked_sources;
      var new_sources = vm.sourceFormData.new_sources;
      var linked_destinations = vm.destinationFormData.linked_destinations;
      var new_destinations = vm.destinationFormData.new_destinations;
      var linked_applications = vm.serviceFormData.linked_applications;
      var new_applications = vm.serviceFormData.new_applications;
      var linked_services = vm.serviceFormData.linked_services;
      var new_services = vm.serviceFormData.new_services;
      
      // source addrs
      for (var k in linked_sources) {
        policy.source_addresses.push(linked_sources[k]);
        linked_objects.source_addresses[linked_sources[k].value] = linked_sources[k];
      }
      for (var k in new_sources) {
        policy.source_addresses.push(new_sources[k]);
        new_objects.source_addresses[new_sources[k].value] = new_sources[k];
      }
      
      // source zones
      for (k in vm.sourceFormData.zones) {
        policy.source_zones.push(vm.sourceFormData.zones[k]);
      }
      for (k in vm.sourceFormData.new_zones) {
        policy.source_zones.push(vm.sourceFormData.new_zones[k]);
      }

      // destination addrs
      for (var k in linked_destinations) {
        policy.destination_addresses.push(linked_destinations[k]);
        linked_objects.destination_addresses[linked_destinations[k].value] = linked_destinations[k];
      }
      for (var k in new_destinations) {
        policy.destination_addresses.push(new_destinations[k]);
        new_objects.destination_addresses[new_destinations[k].value] = new_destinations[k];
      }

      // destination zones
      for (k in vm.destinationFormData.zones) {
        policy.destination_zones.push(vm.destinationFormData.zones[k]);
      }
      for (k in vm.destinationFormData.new_zones) {
        policy.destination_zones.push(vm.destinationFormData.new_zones[k]);
      }

      // applicaitons
      for (var k in linked_applications) {
        policy.applications.push(linked_applications[k]);
        linked_objects.applications[linked_applications[k].name] = linked_applications[k];
      }
      for (var k in new_applications) {
        policy.applications.push(new_applications[k]);
        // applications are a special case, as we don't actually create "new" ones
        linked_objects.applications[new_applications[k].name] = new_applications[k];
      }

      // services
      for (var k in linked_services) {
        policy.services.push(linked_services[k]);
        linked_objects.services[linked_services[k].protocol + '/' + linked_services[k].port] = linked_services[k];
      }
      for (var k in new_services) {
        policy.services.push(new_services[k]);
        new_objects.services[new_services[k].protocol + '/' + new_services[k].port] = new_services[k];
      }

      // now update the candidate policy object
      candidate_policy.policy = policy;
      candidate_policy.linked_objects = linked_objects;
      candidate_policy.new_objects = new_objects;
      candidate_policy.method = 'NEW_POLICY';

      candidatePolicyService.updateCandidatePolicy(candidate_policy);

      console.log(candidate_policy);

      $location.path('changeRequest/' + $stateParams.id + '/confirm');

    }

    vm.addNewZone = function(list){
      var instance = "";
      list.splice(list.length,0,instance);
    };

    vm.addNewApplication = function(list){
      var instance = {name:null};
      list.splice(list.length,0,instance);
    };

    vm.removeFromList = function($event,index, list){
      if($event.which == 1){
        list.splice(index, 1);
      }
    };

    vm.addNewAddress = function(list){
      var instance = {name: null, type: null, value: null};
      list.splice(list.length,0,instance);
    };


  }
})();
