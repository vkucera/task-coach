//
//  TwoWayModifiedTasksState.h
//  TaskCoach
//
//  Created by Jérôme Laheurte on 01/02/09.
//  Copyright 2009 Jérôme Laheurte. See COPYING for details.
//

#import "EntityUploadState.h"

@interface TwoWayModifiedTasksState : EntityUploadState
{
}

+ stateWithNetwork:(Network *)network controller:(SyncViewController *)controller;

@end
