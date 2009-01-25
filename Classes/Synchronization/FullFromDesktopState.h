//
//  FullFromDesktopState.h
//  TaskCoach
//
//  Created by Jérôme Laheurte on 25/01/09.
//  Copyright 2009 __MyCompanyName__. All rights reserved.
//

#import <Foundation/Foundation.h>

#import "BaseState.h"

@interface FullFromDesktopState : BaseState <State>
{
	NSInteger state;
	NSInteger categoryCount;
	NSInteger taskCount;
	NSInteger doneCount;
	
	NSString *categoryName;
	
	NSString *taskSubject;
	NSString *taskId;
	NSString *taskDescription;
	NSString *taskStart;
	NSString *taskDue;
	NSString *taskCompleted;
	NSNumber *taskCategoryId;
}

@end
