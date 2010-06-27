//
//  TaskCellBig.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 22/02/09.
//  Copyright 2009 Jérôme Laheurte. See COPYING for details.
//

#import "CDTask+Addons.h"
#import "CDTask.h"
#import "CDCategory.h"
#import "TaskCellBig.h"
#import "String+Utils.h"
#import "DateUtils.h"
#import "i18n.h"

@implementation TaskCellBig

@synthesize infosLabel;
@synthesize categoriesLabel;

- (NSString *)trackingLedName
{
	return @"ledclockbig.png";
}

- (NSString *)completedLedName
{
	return @"ledgreenbig.png";
}

- (NSString *)overdueLedName
{
	return @"ledredbig.png";
}

- (NSString *)dueSoonLedName
{
	return @"ledorangebig.png";
}

- (NSString *)startedLedName
{
	return @"ledbluebig.png";
}

- (NSString *)notStartedLedName
{
	return @"ledgreybig.png";
}

- (void)dealloc
{
	[infosLabel release];
	[categoriesLabel release];
	
	[super dealloc];
}

- (void)setTask:(CDTask *)task target:(id)theTarget action:(SEL)theAction
{
	[super setTask:task target:theTarget action:theAction];
	
	NSMutableArray *categories = [[NSMutableArray alloc] init];
	for (CDCategory *cat in task.categories)
		[categories addObject:cat.name];
	categoriesLabel.text = [@", " stringByJoiningStrings:categories];
	[categories release];

	infosLabel.text = @"";
	
	switch ([[task dateStatus] intValue])
	{
		case TASKSTATUS_COMPLETED:
			infosLabel.text = [NSString stringWithFormat:_("Completed %@"), [[UserTimeUtils instance] stringFromDate:task.completionDate]];
			break;
		case TASKSTATUS_OVERDUE:
			infosLabel.text = [NSString stringWithFormat:_("Due %@"), [[UserTimeUtils instance] stringFromDate:task.dueDate]];
			break;
		case TASKSTATUS_DUESOON:
			infosLabel.text = [NSString stringWithFormat:_("Due %@"), [[UserTimeUtils instance] stringFromDate:task.dueDate]];
			break;
		case TASKSTATUS_STARTED:
			if (task.dueDate)
				infosLabel.text = [NSString stringWithFormat:_("Due %@"), [[UserTimeUtils instance] stringFromDate:task.dueDate]];
		case TASKSTATUS_NOTSTARTED:
			if (task.startDate)
				infosLabel.text = [NSString stringWithFormat:_("Start %@"), [[UserTimeUtils instance] stringFromDate:task.startDate]];
			break;
	}
}

@end
