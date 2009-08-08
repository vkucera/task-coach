//
//  Task.h
//  TaskCoach
//
//  Created by Jérôme Laheurte on 14/01/09.
//  Copyright 2009 Jérôme Laheurte. See COPYING for details.
//

#import <Foundation/Foundation.h>
#import "DomainObject.h"

@class Category;

#define TASKSTATUS_OVERDUE           0
#define TASKSTATUS_DUETODAY          1
#define TASKSTATUS_STARTED           2
#define TASKSTATUS_NOTSTARTED        3
#define TASKSTATUS_COMPLETED         4

@interface Task : DomainObject
{
	NSString *description;
	NSString *startDate;
	NSString *dueDate;
	NSString *completionDate;
	
	BOOL hasCat;
}

@property (nonatomic, retain) NSString *description;
@property (nonatomic, retain) NSString *startDate;
@property (nonatomic, retain) NSString *dueDate;
@property (nonatomic, retain) NSString *completionDate;

- initWithId:(NSInteger)ID name:(NSString *)name status:(NSInteger)status taskCoachId:(NSString *)taskCoachId description:(NSString *)description
   startDate:(NSString *)startDate dueDate:(NSString *)dueDate completionDate:(NSString *)completionDate;

- (NSInteger)taskStatus;
- (void)setCompleted:(BOOL)completed;

- (BOOL)hasCategory:(Category *)category;
- (void)removeCategory:(Category *)category;
- (void)addCategory:(Category *)category;

@end
