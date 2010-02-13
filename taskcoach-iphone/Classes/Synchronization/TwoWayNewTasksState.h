//
//  TwoWayNewTasksState.h
//  TaskCoach
//
//  Created by Jérôme Laheurte on 01/02/09.
//  Copyright 2009 Jérôme Laheurte. See COPYING for details.
//

#import <Foundation/Foundation.h>

#import "UploadObjectsState.h"

@interface TwoWayNewTasksState : UploadObjectsState
{
	NSMutableArray *taskCategories;
	NSString *parentId;
}

@end
