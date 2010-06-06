//
//  TwoWayModifiedCategoriesState.h
//  TaskCoach
//
//  Created by Jérôme Laheurte on 23/08/09.
//  Copyright 2009 __MyCompanyName__. All rights reserved.
//

#import "EntityUploadState.h"

@interface TwoWayModifiedCategoriesState : EntityUploadState
{
}

+ stateWithNetwork:(Network *)network controller:(SyncViewController *)controller;

@end
