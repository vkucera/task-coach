//
//  CategoryTaskViewController.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 30/05/10.
//  Copyright 2010 Jérôme Laheurte. All rights reserved.
//

#import "TaskCoachAppDelegate.h"
#import "CategoryViewController.h"
#import "CategoryTaskViewController.h"
#import "TaskDetailsControlleriPad.h"
#import "TaskDetailsController.h"
#import "String+Utils.h"
#import "Configuration.h"

#import "CDTask.h"
#import "CDTask+Addons.h"
#import "CDHierarchicalDomainObject+Addons.h"
#import "CDDomainObject+Addons.h"
#import "CDFile.h"

#import "i18n.h"

@implementation CategoryTaskViewController

- initWithCategoryController:(CategoryViewController *)controller edit:(BOOL)edit category:(CDCategory *)theCategory
{
	if ((self = [super initWithCategoryController:controller edit:edit]))
	{
		category = [theCategory retain];
	}

	return self;
}

- (void)setCategory:(CDCategory *)theCategory
{
	// This is only used on the iPad

	[self.navigationController popToRootViewControllerAnimated:YES];

	[category release];
	category = [theCategory retain];

	if (category)
		self.navigationItem.title = category.name;
	else
		self.navigationItem.title = _("All");

	[self populate];
	[self.tableView reloadData];
}

- (BOOL)compareCategory:(CDCategory *)aCategory
{
	return [[[aCategory objectID] URIRepresentation] isEqual:[[category objectID] URIRepresentation]];
}

- (void)dealloc
{
	[category release];
	[super dealloc];
}

- (void)viewDidLoad
{
	[super viewDidLoad];

	if (category)
		self.navigationItem.title = category.name;
	else
		self.navigationItem.title = _("All");
}

- (void)viewWillAppear:(BOOL)animated
{
	[super viewWillAppear:animated];
	
	[self populate];
}

- (NSPredicate *)predicate
{
	if (category)
		return [NSPredicate predicateWithFormat:@"parent == NULL AND ANY categories IN %@", [category selfAndChildren]];
	else
		return [NSPredicate predicateWithFormat:@"parent == NULL"];
}

- (IBAction)onAddTask:(UIBarButtonItem *)button
{
	[super onAddTask:button];

	CDTask *task = (CDTask *)[NSEntityDescription insertNewObjectForEntityForName:@"CDTask" inManagedObjectContext:getManagedObjectContext()];
	task.creationDate = [NSDate date];
	task.file = [Configuration configuration].cdCurrentFile;
	task.name = @"";
	task.longDescription = @"";
	if (category)
		[task addCategoriesObject:category];

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

#pragma mark UISplitViewControllerDelegate methods

- (void)splitViewController:(UISplitViewController*)svc
	 willHideViewController:(UIViewController *)aViewController
		  withBarButtonItem:(UIBarButtonItem*)barButtonItem
	   forPopoverController:(UIPopoverController*)pc
{
	[barButtonItem setTitle:_("Categories")];
	NSMutableArray *items = [[NSMutableArray alloc] init];
	[items addObject:barButtonItem];
	[items addObjectsFromArray:[self.toolbar items]];
	[self.toolbar setItems:items animated:YES];
	[pc setPopoverContentSize:CGSizeMake(400, 920)];
	popCtrl = pc;
}

- (void)splitViewController:(UISplitViewController*)svc
	 willShowViewController:(UIViewController *)aViewController
  invalidatingBarButtonItem:(UIBarButtonItem *)button
{
	NSMutableArray *items = [[NSMutableArray alloc] init];
	for (UIBarItem *item in [self.toolbar items])
	{
		if (item != button)
			[items addObject:item];
	}
	[self.toolbar setItems:items animated:YES];
	popCtrl = nil;
}

- (void)splitViewController:(UISplitViewController*)svc
		  popoverController:(UIPopoverController*)pc
  willPresentViewController:(UIViewController *)aViewController
{
	if (groupSheet)
	{
		[groupSheet dismissWithClickedButtonIndex:-1 animated:YES];
		groupSheet = nil;
	}
}

@end
