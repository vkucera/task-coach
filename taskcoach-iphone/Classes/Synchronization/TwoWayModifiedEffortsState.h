//
//  TwoWayModifiedEffortsState.h
//  TaskCoach
//
//  Created by Jérôme Laheurte on 22/01/10.
//  Copyright 2010 Jérôme Laheurte. All rights reserved.
//

#import "EntityUploadState.h"

@interface TwoWayModifiedEffortsState : EntityUploadState
{
}

+ stateWithNetwork:(Network *)network controller:(SyncViewController *)controller;

@end
