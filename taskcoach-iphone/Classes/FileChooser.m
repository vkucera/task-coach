//
//  FileChooser.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 25/12/09.
//  Copyright 2009 Jérôme Laheurte. All rights reserved.
//

#import "TaskCoachAppDelegate.h"
#import "FileChooser.h"
#import "CategoryViewController.h"
#import "Configuration.h"
#import "i18n.h"
#import "LogUtils.h"

#import "CDFile.h"
#import "CDDomainObject.h"
#import "CDDomainObject+Addons.h"

@implementation FileChooser

- initWithController:(CategoryViewController *)ctrl
{
	if ((self = [super initWithNibName:@"FileChooser" bundle:[NSBundle mainBundle]]))
	{
		catCtrl = ctrl;

		NSFetchRequest *request = [[NSFetchRequest alloc] init];
		[request setEntity:[NSEntityDescription entityForName:@"CDFile" inManagedObjectContext:getManagedObjectContext()]];
		NSSortDescriptor *sd = [[NSSortDescriptor alloc] initWithKey:@"name" ascending:YES];
		[request setSortDescriptors:[NSArray arrayWithObject:sd]];
		[sd release];

		resultsCtrl = [[NSFetchedResultsController alloc] initWithFetchRequest:request managedObjectContext:getManagedObjectContext() sectionNameKeyPath:nil cacheName:@"CDFileCache"];
		[request release];
		
		NSError *error;
		if (![resultsCtrl performFetch:&error])
		{
			UIAlertView *alert = [[UIAlertView alloc] initWithTitle:@"Error" message:@"Could not load files" delegate:self cancelButtonTitle:@"OK" otherButtonTitles:nil];
			[alert show];
			[alert release];
		}
	}
	
	return self;
}

- (void)viewDidLoad
{
	[super viewDidLoad];

	[self setEditing:YES];
}

- (void)dealloc
{
	[catCtrl loadCategories];
	[catCtrl.tableView reloadData];

	if (UI_USER_INTERFACE_IDIOM() == UIUserInterfaceIdiomPad)
	{
		[catCtrl selectAll];
	}

	[resultsCtrl release];

	[super dealloc];
}

- (BOOL)shouldAutorotateToInterfaceOrientation:(UIInterfaceOrientation)toInterfaceOrientation
{
	return YES;
}

#pragma mark Table view methods

- (NSInteger)numberOfSectionsInTableView:(UITableView *)tableView
{
    return [[resultsCtrl sections] count];
}

- (NSInteger)tableView:(UITableView *)tableView numberOfRowsInSection:(NSInteger)section
{
	return [[[resultsCtrl sections] objectAtIndex:section] numberOfObjects];
}

- (UITableViewCell *)tableView:(UITableView *)tableView cellForRowAtIndexPath:(NSIndexPath *)indexPath
{
    static NSString *CellIdentifier = @"Cell";
    
    UITableViewCell *cell = [tableView dequeueReusableCellWithIdentifier:CellIdentifier];
    if (cell == nil)
	{
        cell = [[[UITableViewCell alloc] initWithStyle:UITableViewCellStyleDefault reuseIdentifier:CellIdentifier] autorelease];
    }

	CDFile *file = [resultsCtrl objectAtIndexPath:indexPath];
	cell.textLabel.text = file.name;
	if (file == [Configuration configuration].cdCurrentFile)
		cell.editingAccessoryType = UITableViewCellAccessoryCheckmark;
	else
		cell.editingAccessoryType = UITableViewCellAccessoryNone;

    return cell;
}

- (void)tableView:(UITableView *)tableView didSelectRowAtIndexPath:(NSIndexPath *)indexPath
{
	[Configuration configuration].cdCurrentFile = [resultsCtrl objectAtIndexPath:indexPath];
	[[Configuration configuration] save];

	[self.tableView reloadData];

	if (UI_USER_INTERFACE_IDIOM() == UIUserInterfaceIdiomPad)
		[catCtrl.splitCtrl dismissModalViewControllerAnimated:YES];
	else
		[catCtrl.navigationController dismissModalViewControllerAnimated:YES];
}

- (void)tableView:(UITableView *)tableView commitEditingStyle:(UITableViewCellEditingStyle)editingStyle forRowAtIndexPath:(NSIndexPath *)indexPath
{
	if (editingStyle == UITableViewCellEditingStyleDelete)
	{
		CDFile *file = [resultsCtrl objectAtIndexPath:indexPath];
		NSMutableArray *results = [[NSMutableArray alloc] init];

		for (NSString *name in [NSArray arrayWithObjects:@"CDTask", @"CDCategory", @"CDEffort", nil])
		{
			NSFetchRequest *request = [[NSFetchRequest alloc] init];
			[request setEntity:[NSEntityDescription entityForName:name inManagedObjectContext:getManagedObjectContext()]];
			[request setPredicate:[NSPredicate predicateWithFormat:@"file == %@", file]];
			NSError *error;
			NSArray *objs = [getManagedObjectContext() executeFetchRequest:request error:&error];

			if (objs)
			{
				[results addObjectsFromArray:objs];
			}
			else
			{
				JLERROR("Could not fetch objects: %s", [[error localizedDescription] UTF8String]);
				assert(0);
			}

			[request release];
		}

		for (CDDomainObject *object in results)
			[getManagedObjectContext() deleteObject:object];

		[results release];
		[getManagedObjectContext() deleteObject:file];
		
		NSError *error;
		if (![getManagedObjectContext() save:&error])
		{
			UIAlertView *alert = [[UIAlertView alloc] initWithTitle:@"Error" message:@"Could not save data" delegate:self cancelButtonTitle:@"OK" otherButtonTitles:nil];
			[alert show];
			[alert release];
		}

		NSFetchRequest *request = [[NSFetchRequest alloc] init];
		[request setEntity:[NSEntityDescription entityForName:@"CDFile" inManagedObjectContext:getManagedObjectContext()]];
		NSArray *files = [getManagedObjectContext() executeFetchRequest:request error:&error];
		[request release];

		if (files)
		{
			if ([files count] <= 1)
			{
				if ([files count])
					[Configuration configuration].cdCurrentFile = [files objectAtIndex:0];
				else
					[Configuration configuration].cdCurrentFile = nil;
				
				[[Configuration configuration] save];
				
				if (UI_USER_INTERFACE_IDIOM() == UIUserInterfaceIdiomPad)
					[catCtrl.splitCtrl dismissModalViewControllerAnimated:YES];
				else
					[catCtrl.navigationController dismissModalViewControllerAnimated:YES];
			}
		}
		else
		{
			JLERROR("Could not fetch files: %s", [[error localizedDescription] UTF8String]);
			assert(0);
		}
	}
}

@end

