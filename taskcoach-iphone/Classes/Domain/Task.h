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
	NSDate *startDate;
	NSDate *dueDate;
	NSDate *completionDate;
}

- initWithId:(NSInteger)ID name:(NSString *)name status:(NSInteger)status startDate:(NSDate *)startDate dueDate:(NSDate *)dueDate completionDate:(NSDate *)completionDate;

@end
