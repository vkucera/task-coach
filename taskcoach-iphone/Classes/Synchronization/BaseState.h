//
//  BaseState.h
//  TaskCoach
//
//  Created by Jérôme Laheurte on 24/01/09.
//  Copyright 2009 Jérôme Laheurte. See COPYING for details.
//

#import <Foundation/Foundation.h>

#import "State.h"

@interface BaseState : NSObject
{
	Network *myNetwork;
	SyncViewController *myController;
}

- (void)sendDate:(NSDate *)date;
- (NSDate *)parseDate:(id)date;

- initWithNetwork:(Network *)network controller:(SyncViewController *)controller;

- (void)networkDidClose:(Network *)network controller:(SyncViewController *)controller;
- (void)networkDidEncounterError:(Network *)network error:(NSError *)error controller:(SyncViewController *)controller;

- (void)cancel;

@end
