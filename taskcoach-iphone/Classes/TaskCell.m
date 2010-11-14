//
//  TaskCell.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 17/01/09.
//  Copyright 2009 Jérôme Laheurte. See COPYING for details.
//

#import "TaskCell.h"
#import "CheckView.h"

#import "CDTask.h"
#import "CDTask+Addons.h"

@implementation TaskCell

@synthesize task;
@synthesize leftImage;
@synthesize titleLabel;

- (NSString *)trackingLedName
{
	return @"ledclock.png";
}

- (NSString *)completedLedName
{
	return @"green.png";
}

- (NSString *)overdueLedName
{
	return @"red.png";
}

- (NSString *)dueSoonLedName
{
	return @"orange.png";
}

- (NSString *)startedLedName
{
	return @"blue.png";
}

- (NSString *)notStartedLedName
{
	return @"grey.png";
}

- (void)setTask:(CDTask *)theTask target:(id)theTarget action:(SEL)theAction
{
	self.task = theTask;

	target = theTarget;
	action = theAction;

	titleLabel.text = task.name;

	if ([task currentEffort])
	{
		leftImage.image = [UIImage imageNamed:[self trackingLedName]];
	}
	else
	{
		NSString *suffix = nil;

		switch ([[task dateStatus] intValue])
		{
			case TASKSTATUS_COMPLETED:
				suffix = [self completedLedName];
				break;
			case TASKSTATUS_OVERDUE:
				suffix = [self overdueLedName];
				break;
			case TASKSTATUS_DUESOON:
				suffix = [self dueSoonLedName];
				break;
			case TASKSTATUS_STARTED:
				suffix = [self startedLedName];
				break;
			case TASKSTATUS_NOTSTARTED:
				suffix = [self notStartedLedName];
				//leftImage.image = [UIImage imageNamed:[self notStartedLedName]];
				break;
			default:
				break;
		}

		if ([theTask.children count])
			leftImage.image = [UIImage imageNamed:[NSString stringWithFormat:@"folder%@", suffix]];
		else
			leftImage.image = [UIImage imageNamed:[NSString stringWithFormat:@"led%@", suffix]];
	}

	[leftImage setTarget:self action:@selector(onTapImage)];

	if ([[task children] count])
	{
		self.accessoryType = UITableViewCellAccessoryDetailDisclosureButton;
	}
	else
	{
		self.accessoryType = UITableViewCellAccessoryNone;
	}

	self.editingAccessoryType = UITableViewCellAccessoryDetailDisclosureButton;
}

- (void)dealloc
{
	[leftImage release];
	[titleLabel release];
	[task release];

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
		[super setSelected:NO animated:NO];
	}
	else
	{
		[super setSelected:selected animated:animated];
	}
}

@end
