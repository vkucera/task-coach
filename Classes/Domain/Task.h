//
//  Task.h
//  TaskCoach
//
//  Created by Jérôme Laheurte on 14/01/09.
//  Copyright 2009 __MyCompanyName__. All rights reserved.
//

#import <Foundation/Foundation.h>
#import "DomainObject.h"

@interface Task : DomainObject
{
	NSString *description;
	NSDate *startDate;
	NSDate *dueDate;
	NSDate *completionDate;
}

@property (nonatomic, retain) NSString *description;
@property (nonatomic, retain) NSDate *startDate;
@property (nonatomic, retain) NSDate *dueDate;
@property (nonatomic, retain) NSDate *completionDate;

- initWithId:(NSInteger)ID name:(NSString *)name status:(NSInteger)status description:(NSString *)description startDate:(NSDate *)startDate dueDate:(NSDate *)dueDate completionDate:(NSDate *)completionDate;

@end
