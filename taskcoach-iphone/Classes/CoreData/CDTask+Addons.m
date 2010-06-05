//
//  CDTask+Addons.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 30/05/10.
//  Copyright 2010 Jérôme Laheurte. All rights reserved.
//

#import "CDTask+Addons.h"
#import "Configuration.h"

@implementation CDTask (Addons)

- (void)computeDateStatus
{
	if (self.completionDate)
	{
		self.dateStatus = [NSNumber numberWithInt:TASKSTATUS_COMPLETED];
		return;
	}

	if (self.dueDate)
	{
		NSTimeInterval diff = [self.dueDate timeIntervalSinceDate:[NSDate date]];
		if (diff < 0)
		{
			self.dateStatus = [NSNumber numberWithInt:TASKSTATUS_OVERDUE];
			return;
		}

		if (diff < 24 * 60 * 60 * [Configuration configuration].soonDays)
		{
			self.dateStatus = [NSNumber numberWithInt:TASKSTATUS_DUESOON];
			return;
		}
	}

	if (self.startDate)
	{
		NSLog(@"TI: %.2f", [self.startDate timeIntervalSinceDate:[NSDate date]]);

		if ([self.startDate timeIntervalSinceDate:[NSDate date]] < 0)
		{
			self.dateStatus = [NSNumber numberWithInt:TASKSTATUS_STARTED];
			return;
		}
	}

	self.dateStatus = [NSNumber numberWithInt:TASKSTATUS_NOTSTARTED];
}

@end
