//
//  TaskList.h
//  TaskCoach
//
//  Created by Jérôme Laheurte on 15/01/09.
//  Copyright 2009 __MyCompanyName__. All rights reserved.
//

#import <Foundation/Foundation.h>

@class Statement;
@class Task;

#define TASKSTATUS_OVERDUE           0
#define TASKSTATUS_DUETODAY          1
#define TASKSTATUS_STARTED           2
#define TASKSTATUS_NOTSTARTED        3
#define TASKSTATUS_COMPLETED         4

@interface TaskList : NSObject
{
	NSMutableArray *tasks;
	NSInteger firstIndex;
	Statement *request;
	Statement *countRequest;
	NSInteger count;
	NSString *title;
	NSInteger status;
}

@property (nonatomic, readonly) NSInteger count;
@property (nonatomic, readonly) NSString *title;
@property (nonatomic, readonly) NSInteger status;

- initWithView:(NSString *)viewName category:(NSInteger)categoryId title:(NSString *)title status:(NSInteger)status;

- (Task *)taskAtIndex:(NSInteger)index;
- (void)reload;

@end
