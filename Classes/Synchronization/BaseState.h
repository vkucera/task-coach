//
//  BaseState.h
//  TaskCoach
//
//  Created by Jérôme Laheurte on 24/01/09.
//  Copyright 2009 __MyCompanyName__. All rights reserved.
//

#import <Foundation/Foundation.h>

#import "State.h"

@interface BaseState : NSObject
{
	Network *myNetwork;
	SyncViewController *myController;
}

- initWithNetwork:(Network *)network controller:(SyncViewController *)controller;

- (void)networkDidClose:(Network *)network controller:(SyncViewController *)controller;
- (void)networkDidEncounterError:(Network *)network controller:(SyncViewController *)controller;

@end
