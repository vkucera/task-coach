//
//  ParentTaskViewController.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 05/06/10.
//  Copyright 2010 Jérôme Laheurte. All rights reserved.
//

#import "ParentTaskViewController.h"
#import "TaskDetailsController.h"
#import "TaskDetailsControlleriPad.h"
#import "TaskCoachAppDelegate.h"
#import "i18n.h"
#import "CDTask+Addons.h"
#import "CDDomainObject+Addons.h"
#import "CDFile.h"
#import "Configuration.h"

@implementation ParentTaskViewController

- initWithCategoryController:(CategoryViewController *)controller edit:(BOOL)edit parent:(CDTask *)theParent
{
	if ((self = [super initWithCategoryController:controller edit:edit]))
	{
		parent = [theParent retain];

		[self populate];
	}

	return self;
}

- (void)dealloc
{
	[parent release];
	[super dealloc];
}

- (void)viewDidLoad
{
	[super viewDidLoad];

	self.navigationItem.title = parent.name;
}

- (NSPredicate *)predicate
{
	return [NSPredicate predicateWithFormat:@"parent == %@", parent];
}

- (IBAction)onAddTask:(UIBarButtonItem *)button
{
	[super onAddTask:button];
	
	CDTask *task = (CDTask *)[NSEntityDescription insertNewObjectForEntityForName:@"CDTask" inManagedObjectContext:getManagedObjectContext()];
	
	task.creationDate = [NSDate date];
	task.file = [Configuration configuration].cdCurrentFile;
	task.name = @"";
	task.longDescription = @"";
	task.parent = parent;
	
	// Current date, day start hour
	NSDateComponents *components = [[NSCalendar currentCalendar] components:NSYearCalendarUnit|NSMonthCalendarUnit|NSDayCalendarUnit fromDate:[NSDate date]];
	[components setHour:[[Configuration configuration].cdCurrentFile.startHour intValue]];
	[components setMinute:0];
	[components setSecond:0];
	task.startDate = [[NSCalendar currentCalendar] dateFromComponents:components];

	[task computeDateStatus];

	if ([task save])
	{
		UIViewController *ctrl;
		
		if (UI_USER_INTERFACE_IDIOM() == UIUserInterfaceIdiomPhone)
			ctrl = [[TaskDetailsController alloc] initWithTask:task];
		else
			ctrl = [[TaskDetailsControlleriPad alloc] initWithTask:task];

		[self.navigationController pushViewController:ctrl animated:YES];
		[ctrl release];
	}
}

@end
