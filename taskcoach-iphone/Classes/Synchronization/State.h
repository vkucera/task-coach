//
//  State.h
//  TaskCoach
//
//  Created by Jérôme Laheurte on 24/01/09.
//  Copyright 2009 Jérôme Laheurte. See COPYING for details.
//

#import <Foundation/Foundation.h>

@class SyncViewController;
@class Network;

@protocol State

+ stateWithNetwork:(Network *)network controller:(SyncViewController *)controller;

- (void)activated;

- (void)networkDidConnect:(Network *)network controller:(SyncViewController *)controller;
- (void)networkDidClose:(Network *)network controller:(SyncViewController *)controller;
- (void)networkDidEncounterError:(Network *)network error:(NSError *)error controller:(SyncViewController *)controller;
- (void)network:(Network *)network didGetData:(NSData *)data controller:(SyncViewController *)controller;

- (void)cancel;

@end
