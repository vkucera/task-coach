//
//  TaskCell.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 17/01/09.
//  Copyright 2009 __MyCompanyName__. All rights reserved.
//

#import "TaskCell.h"

#import "Task.h"
#import "TaskList.h"

@implementation TaskCell

@synthesize leftImage;
@synthesize titleLabel;
@synthesize infosLabel;

- (void)setTask:(Task *)task
{
	titleLabel.text = task.name;

	switch ([task taskStatus])
	{
		case TASKSTATUS_OVERDUE:
			infosLabel.text = [NSString stringWithFormat:NSLocalizedString(@"Due %@", @"Due date infos pattern"), task.dueDate];
			break;
		case TASKSTATUS_DUETODAY:
			infosLabel.text = [NSString stringWithFormat:NSLocalizedString(@"Started %@", @"Start date infos pattern"), task.startDate];
			break;
		case TASKSTATUS_STARTED:
		case TASKSTATUS_NOTSTARTED:
			if ([task dueDate])
				infosLabel.text = [NSString stringWithFormat:NSLocalizedString(@"Due %@", @"Due date infos pattern (started/not started)"), task.dueDate];
			else
				infosLabel.text = @"";
			break;
		default:
			infosLabel.text = @"";
			break;
	}
	
	switch ([task taskStatus])
	{
		case TASKSTATUS_OVERDUE:
			leftImage.image = [UIImage imageNamed:@"ledred.png"];
			break;
		case TASKSTATUS_DUETODAY:
			leftImage.image = [UIImage imageNamed:@"ledorange.png"];
			break;
		case TASKSTATUS_STARTED:
			leftImage.image = [UIImage imageNamed:@"ledblue.png"];
			break;
		case TASKSTATUS_NOTSTARTED:
			leftImage.image = [UIImage imageNamed:@"ledgrey.png"];
			break;
		case TASKSTATUS_COMPLETED:
			leftImage.image = [UIImage imageNamed:@"ledgreen.png"];
			break;
		default:
			break;
	}
}

- (void)dealloc
{
	[leftImage release];
	[titleLabel release];
	[infosLabel release];

	[super dealloc];
}

@end
