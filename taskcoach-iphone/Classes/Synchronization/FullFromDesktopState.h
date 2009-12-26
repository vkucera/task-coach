//
//  FullFromDesktopState.h
//  TaskCoach
//
//  Created by Jérôme Laheurte on 25/01/09.
//  Copyright 2009 Jérôme Laheurte. See COPYING for details.
//

#import <Foundation/Foundation.h>

#import "BaseState.h"

@interface FullFromDesktopState : BaseState <State>
{
	NSMutableDictionary *idMap;

	NSInteger state;
	NSInteger categoryCount;
	NSInteger taskCount;
	NSInteger doneCount;
	NSInteger total;
	
	NSString *categoryName;
	NSString *categoryId;
	
	NSString *taskSubject;
	NSString *taskId;
	NSString *taskDescription;
	NSString *taskStart;
	NSString *taskDue;
	NSString *taskCompleted;
	
	NSInteger taskCategoryCount;
	NSInteger taskLocalId;
	NSInteger parentLocalId;
}

@end
