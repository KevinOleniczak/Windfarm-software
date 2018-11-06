'use strict';

// The sumerian object can be used to access Sumerian engine
// types.
//
/* global sumerian */

function sleep(ms) {
  return new Promise((resolve, reject) => setTimeout(resolve, ms));
}

// Called when play mode starts.
//
function setup(args, ctx) {
	// Initialize this value at scene start to ensure it is never undefined.
	// ctx.entityData is shared by all scripts attached to an entity, either
	// through a script action or the script component.
	//ctx.entityData.turbine_speed = 10; // Don't start with zero as it will cause a division by zero error.
}

function enter(args, ctx) {

	if (ctx.entityData.turbine_speed !== '0.0') {
		var rpm = ctx.entityData.turbine_speed;
	} else {
		var rpm = 10;
	}

	sleep(60/(rpm/36)).then(() => {});

	return ctx.transitions.success();
}

// When used in a ScriptAction, called when a state is exited.
//
function exit(args, ctx) {
}

var parameters = [];
