//
//  State.h
//  TaskCoach
//
//  Created by Jérôme Laheurte on 24/01/09.
//  Copyright 2009 __MyCompanyName__. All rights reserved.
//

#import <Foundation/Foundation.h>

@class SyncViewController;
@class Network;

@protocol State

+ stateWithNetwork:(Network *)network controller:(SyncViewController *)controller;

- (void)networkDidConnect:(Network *)network controller:(SyncViewController *)controller;
- (void)networkDidClose:(Network *)network controller:(SyncViewController *)controller;
- (void)networkDidEncounterError:(Network *)network controller:(SyncViewController *)controller;
- (void)network:(Network *)network didGetData:(NSData *)data controller:(SyncViewController *)controller;

@end
