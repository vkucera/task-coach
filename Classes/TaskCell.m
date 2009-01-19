//
//  TaskCell.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 17/01/09.
//  Copyright 2009 __MyCompanyName__. All rights reserved.
//

#import "TaskCell.h"
#import "CheckView.h"

#import "Task.h"
#import "TaskList.h"

@implementation TaskCell

@synthesize taskId;
@synthesize leftImage;
@synthesize titleLabel;
@synthesize infosLabel;

- (void)setTask:(Task *)task target:(id)theTarget action:(SEL)theAction
{
	taskId = task.objectId;
	target = theTarget;
	action = theAction;

	titleLabel.text = task.name;

	switch ([task taskStatus])
	{
		case TASKSTATUS_COMPLETED:
			infosLabel.text = [NSString stringWithFormat:NSLocalizedString(@"Completed %@", @"Completed date infos patter"), task.completionDate];
			break;
		case TASKSTATUS_OVERDUE:
			infosLabel.text = [NSString stringWithFormat:NSLocalizedString(@"Due %@", @"Due date infos pattern"), task.dueDate];
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
		case TASKSTATUS_COMPLETED:
			leftImage.image = [UIImage imageNamed:@"ledgreen.png"];
			break;
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
		default:
			break;
	}
	
	[leftImage setTarget:self action:@selector(onTapImage)];
}

- (void)dealloc
{
	[leftImage release];
	[titleLabel release];
	[infosLabel release];

	[super dealloc];
}

- (void)onTapImage
{
	isTapping = YES;
	[target performSelector:action withObject:self];
}

- (void)setSelected:(BOOL)selected animated:(BOOL)animated
{
	if (isTapping)
	{
		isTapping = NO;
	}
	else
	{
		[super setSelected:selected animated:animated];
	}
}

@end
