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

#define TASKSTATUS_UNDEFINED         0
#define TASKSTATUS_OVERDUE           1
#define TASKSTATUS_DUESOON           2
#define TASKSTATUS_STARTED           3
#define TASKSTATUS_NOTSTARTED        4
#define TASKSTATUS_COMPLETED         5

@interface Task : DomainObject
{
	NSString *description;
	NSString *startDate;
	NSString *dueDate;
	NSString *completionDate;
	
	NSInteger taskStatus;

	NSNumber *parentId;

	BOOL hasCat;
	NSInteger ccount;
}

@property (nonatomic, retain) NSString *description;
@property (nonatomic, retain) NSString *startDate;
@property (nonatomic, retain) NSString *dueDate;
@property (nonatomic, retain) NSString *completionDate;
@property (nonatomic) NSInteger taskStatus;
@property (nonatomic, retain) NSNumber *parentId;

- initWithId:(NSInteger)ID fileId:(NSNumber *)fileId name:(NSString *)name status:(NSInteger)status taskCoachId:(NSString *)taskCoachId description:(NSString *)description
   startDate:(NSString *)startDate dueDate:(NSString *)dueDate completionDate:(NSString *)completionDate dateStatus:(NSInteger)dateStatus parentId:(NSNumber *)parentId;

- (void)setCompleted:(BOOL)completed;

- (BOOL)hasCategory:(Category *)category;
- (void)removeCategory:(Category *)category;
- (void)addCategory:(Category *)category;

- (NSInteger)childrenCount;

@end
