//
//  CDTask+Addons.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 30/05/10.
//  Copyright 2010 Jérôme Laheurte. All rights reserved.
//

#import "CDTask+Addons.h"
#import "CDEffort.h"
#import "Configuration.h"
#import "TaskCoachAppDelegate.h"
#import "DateUtils.h"
#import "CDDomainObject+Addons.h"

@implementation CDTask (Addons)

- (NSDate *)computeNextDate:(NSDate *)date;
{
	NSCalendar *cal = [NSCalendar currentCalendar];
	NSDate *newDate = date;

	if (self.recPeriod != nil)
	{
		switch ([self.recPeriod intValue])
		{
			case REC_DAILY:
			{
				NSDateComponents *comp = [[NSDateComponents alloc] init];
				[comp setDay:[self.recRepeat intValue]];
				newDate = [cal dateByAddingComponents:comp toDate:date options:0];
				[comp release];
				break;
			}
			case REC_WEEKLY:
			{
				NSDateComponents *comp = [[NSDateComponents alloc] init];
				[comp setWeek:[self.recRepeat intValue]];
				newDate = [cal dateByAddingComponents:comp toDate:date options:0];
				break;
			}
			case REC_MONTHLY:
			{
				NSDateComponents *comp = [[NSDateComponents alloc] init];
				[comp setMonth:[self.recRepeat intValue]];
				newDate = [cal dateByAddingComponents:comp toDate:date options:0];
				break;
			}
			case REC_YEARLY:
			{
				NSDateComponents *comp = [[NSDateComponents alloc] init];
				[comp setYear:[self.recRepeat intValue]];
				newDate = [cal dateByAddingComponents:comp toDate:date options:0];
				break;
			}
		}

		if ([self.recSameWeekday intValue])
		{
			switch ([self.recPeriod intValue])
			{
				case REC_MONTHLY:
				case REC_YEARLY:
				{
					NSDateComponents *ref = [cal components:NSWeekdayCalendarUnit fromDate:date];

					while (1)
					{
						NSDateComponents *comp = [cal components:NSWeekdayCalendarUnit fromDate:newDate];
						if ([comp weekday] == [ref weekday])
							break;

						comp = [[NSDateComponents alloc] init];
						[comp setDay:-1];
						newDate = [cal dateByAddingComponents:comp toDate:newDate options:0];
						[comp release];
					}

					break;
				}
			}
		}
	}

	return newDate;
}

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
		if ([self.startDate timeIntervalSinceDate:[NSDate date]] < 0)
		{
			self.dateStatus = [NSNumber numberWithInt:TASKSTATUS_STARTED];
			return;
		}
	}

	self.dateStatus = [NSNumber numberWithInt:TASKSTATUS_NOTSTARTED];
}

- (CDEffort *)currentEffort
{
	for (CDEffort *effort in self.efforts)
	{
		if (!effort.ended)
		{
			return effort;
		}
	}

	return nil;
}

- (void)startTracking
{
	CDEffort *effort = (CDEffort *)[NSEntityDescription insertNewObjectForEntityForName:@"CDEffort" inManagedObjectContext:getManagedObjectContext()];

	effort.file = [Configuration configuration].cdCurrentFile;
	effort.task = self;
	effort.started = [NSDate date];
	effort.ended = nil;
	effort.name = self.name;
}

- (void)stopTracking
{
	CDEffort *effort = [self currentEffort];
	[effort setEnded:[NSDate date]];
	[effort markDirty];
	[effort save];
}

- (NSString *)startDateOnly
{
	if (self.startDate)
		return [[UserDateUtils instance] stringFromDate:self.startDate];
	return @"";
}

- (NSString *)dueDateOnly
{
	if (self.dueDate)
		return [[UserDateUtils instance] stringFromDate:self.dueDate];
	return @"";
}

@end
