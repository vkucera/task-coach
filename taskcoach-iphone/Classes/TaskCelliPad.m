//
//  TaskCelliPad.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 19/06/10.
//  Copyright 2010 Jérôme Laheurte. All rights reserved.
//

#import "TaskCelliPad.h"
#import "CDTask.h"
#import "i18n.h"

@implementation TaskCelliPad

@synthesize priorityLabel;
@synthesize descriptionView;

- (void)dealloc
{
	[priorityLabel release];
	[descriptionView release];

	[super dealloc];
}

- (void)setTask:(CDTask *)task target:(id)theTarget action:(SEL)theAction
{
	[super setTask:task target:theTarget action:theAction];

	priorityLabel.text = [NSString stringWithFormat:_("Priority: %@"), task.priority];
	descriptionView.text = task.longDescription;
}

@end
