//
//  Effort.h
//  TaskCoach
//
//  Created by Jérôme Laheurte on 22/01/10.
//  Copyright 2010 Jérôme Laheurte. All rights reserved.
//

#import "DomainObject.h"
#import "Task.h"

@interface Effort : DomainObject
{
	NSDate *started;
	NSDate *ended;
	NSNumber *taskId;
}

@property (nonatomic, retain) NSDate *started;
@property (nonatomic, retain) NSDate *ended;
@property (nonatomic, readonly) Task *task;

- initWithId:(NSInteger)ID fileId:(NSNumber *)fileId name:(NSString *)name status:(NSInteger)status taskCoachId:(NSString *)taskCoachId started:(NSDate *)started ended:(NSDate *)ended taskId:(NSNumber *)taskId;

@end
