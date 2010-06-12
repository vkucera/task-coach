//
//  CategoryViewController.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 14/01/09.
//  Copyright 2009 Jérôme Laheurte. See COPYING for details.
//

#import "TaskCoachAppDelegate.h"
#import "NavigationController.h"
#import "CategoryViewController.h"
#import "StringChoiceController.h"
#import "CategoryTaskViewController.h"
#import "ParentTaskViewController.h"
#import "SyncViewController.h"
#import "FileChooser.h"
#import "BadgedCell.h"
#import "CellFactory.h"
#import "NSDate+Utils.h"
#import "ReminderController.h"

#import "CDDomainObject+Addons.h"
#import "CDCategory.h"
#import "CDTask.h"
#import "CDTask+Addons.h"
#import "CDHierarchicalDomainObject+Addons.h"

#import "Configuration.h"
#import "i18n.h"

@implementation CategoryViewController

@synthesize navigationController;
@synthesize syncButton;
@synthesize fileButton;

- (void)loadCategories
{
	[super loadCategories];
	
	[self editButtonItem].enabled = ([categories count] != 0);
}

- (void)willTerminate
{
	[[PositionStore instance] push:self indexPath:nil type:0 searchWord:nil];
}

- (void)restorePosition:(Position *)pos store:(PositionStore *)store
{
	[self.tableView setContentOffset:pos.scrollPosition animated:NO];
	
	if (pos.indexPath)
	{
		[self.tableView selectRowAtIndexPath:pos.indexPath animated:NO scrollPosition:UITableViewScrollPositionNone];

		CDCategory *category = nil;

		if (pos.indexPath.row)
		{
			category = [categories objectAtIndex:pos.indexPath.row - 1];
		}

		[[PositionStore instance] push:self indexPath:pos.indexPath type:pos.type searchWord:nil];

		CategoryTaskViewController *ctrl = [[CategoryTaskViewController alloc] initWithCategoryController:self edit:self.editing category:category];
		[self.navigationController pushViewController:ctrl animated:YES];
		[ctrl release];
		
		[store restore:ctrl];
	}
}

- (void)viewDidLoad
{
	[super viewDidLoad];

	NSArray *cachesPaths = NSSearchPathForDirectoriesInDomains(NSCachesDirectory, NSUserDomainMask, YES);
	NSString *cachesDir = [cachesPaths objectAtIndex:0];
	
	NSFileManager *fileManager = [NSFileManager defaultManager];
	if (![fileManager fileExistsAtPath:cachesDir])
	{
		[fileManager createDirectoryAtPath:cachesDir attributes:nil];
	}
	
	NSString *path = [cachesDir stringByAppendingPathComponent:@"positions.store.v4"];
	
	if ([fileManager fileExistsAtPath:path])
	{
		PositionStore *store = [[PositionStore alloc] initWithFile:[cachesDir stringByAppendingPathComponent:@"positions.store.v4"]];
		[store restore:self];
		[store release];
	}
	
	[fileManager release];

	fileButton.enabled = ([Configuration configuration].cdFileCount >= 2);
	
	NSDate *nextUpdate = [NSDate dateRounded];
	nextUpdate = [nextUpdate addTimeInterval:61];
	minuteTimer = [[NSTimer alloc] initWithFireDate:nextUpdate interval:60 target:self selector:@selector(onMinuteTimer:) userInfo:nil repeats:YES];
	[[NSRunLoop currentRunLoop] addTimer:minuteTimer forMode:NSDefaultRunLoopMode];
}

- (void)viewDidUnload
{
	self.navigationController = nil;
	self.syncButton = nil;
	
	[categories release];
	categories = nil;
	
	[indentations release];
	indentations = nil;
	
	[minuteTimer invalidate];
	[minuteTimer release];
	minuteTimer = nil;
}

- (void)dealloc
{
	[self viewDidUnload];
	
	[super dealloc];
}

- (void)onMinuteTimer:(NSTimer *)theTimer
{
	[[ReminderController instance] check];
}

- (void)childWasPopped
{
	NSIndexPath *indexPath = [self.tableView indexPathForSelectedRow];

	[[PositionStore instance] pop];

	if (indexPath)
	{
		[self loadCategories];
		[self.tableView reloadData];
	}
	
	if (wantSync)
	{
		wantSync = NO;
		[self onSynchronize:syncButton];
	}
}

- (void)setWantSync
{
	wantSync = YES;
}

- (IBAction)onChooseFile:(UIBarButtonItem *)button
{
	FileChooser *chooser = [[FileChooser alloc] initWithController:self];
	[self.navigationController presentModalViewController:chooser animated:YES];
	[chooser release];
}

- (IBAction)onAddCategory:(UIBarButtonItem *)button
{
	currentCategory = -1;
	StringChoiceController *ctrl = [[StringChoiceController alloc] initWithPlaceholder:_("Enter category name") text:nil target:self action:@selector(onCategoryAdded:)];
	[self.navigationController presentModalViewController:ctrl animated:YES];
	[ctrl release];
}

- (void)onCategoryAdded:(NSString *)name
{
	if (name != nil)
	{
		CDCategory *newCat = (CDCategory *)[NSEntityDescription insertNewObjectForEntityForName:@"CDCategory" inManagedObjectContext:getManagedObjectContext()];
		if (currentCategory >= 0)
			newCat.parent = [categories objectAtIndex:currentCategory];
		newCat.creationDate = [NSDate date];
		newCat.file = [Configuration configuration].cdCurrentFile;
		newCat.name = name;

		NSError *error;
		if (![getManagedObjectContext() save:&error])
		{
			UIAlertView *alert = [[UIAlertView alloc] initWithTitle:_("Error") message:_("Could not create new category") delegate:self cancelButtonTitle:_("OK") otherButtonTitles:nil];
			[alert show];
			[alert release];
		}

		[self loadCategories];
		[self.tableView reloadData];
	}

	[self.navigationController dismissModalViewControllerAnimated:YES];
	[self.tableView deselectRowAtIndexPath:[self.tableView indexPathForSelectedRow] animated:NO];
}

- (void)fillCell:(BadgedCell *)cell forCategory:(CDCategory *)category
{
	[super fillCell:cell forCategory:category];

	cell.textLabel.text = [category name];

	NSInteger total = [[category task] count];
	NSInteger overdue = 0, dueSoon = 0, started = 0;

	NSFetchRequest *request = [[NSFetchRequest alloc] init];
	[request setEntity:[NSEntityDescription entityForName:@"CDTask" inManagedObjectContext:getManagedObjectContext()]];
	[request setPredicate:[NSPredicate predicateWithFormat:@"status != %d AND ANY categories IN %@ AND parent == NULL", STATUS_DELETED, [category selfAndChildren]]];
	NSError *error;
	NSArray *tasks = [getManagedObjectContext() executeFetchRequest:request error:&error];
	[request release];

	if (tasks)
	{
		for (CDTask *task in tasks)
		{
			switch ([task.dateStatus intValue])
			{
				case TASKSTATUS_OVERDUE:
					overdue++;
					break;
				case TASKSTATUS_DUESOON:
					dueSoon++;
					break;
				case TASKSTATUS_STARTED:
					started++;
					break;
			}
		}
	}
	else
	{
		NSLog(@"Could not fetch tasks: %@", [error localizedDescription]);
	}

	cell.badge.text = [NSString stringWithFormat:@"%d", total];
	cell.badge.capsuleColor = [UIColor blackColor];
	
	if (dueSoon)
		[cell.badge addAnnotation:[NSString stringWithFormat:@"%d", dueSoon] capsuleColor:[UIColor orangeColor]];
	if (overdue)
		[cell.badge addAnnotation:[NSString stringWithFormat:@"%d", overdue] capsuleColor:[UIColor redColor]];
	if (started)
		[cell.badge addAnnotation:[NSString stringWithFormat:@"%d", started] capsuleColor:[UIColor blueColor]];
}

- (void)setEditing:(BOOL)editing animated:(BOOL)animated
{
	syncButton.enabled = !editing;

	[self.tableView beginUpdates];
	
	[super setEditing:editing animated:animated];

	NSMutableArray *indexPaths = [[NSMutableArray alloc] initWithCapacity:[categories count]];
	
	if (editing)
	{
		[self.tableView deleteRowsAtIndexPaths:[NSArray arrayWithObject:[NSIndexPath indexPathForRow:0 inSection:0]] withRowAnimation:UITableViewRowAnimationRight];

		for (NSInteger i = 0; i <= [categories count] - 1; ++i)
		{
			[indexPaths addObject:[NSIndexPath indexPathForRow:2*i+1 inSection:0]];
		}
	
		[self.tableView insertRowsAtIndexPaths:indexPaths withRowAnimation:UITableViewRowAnimationRight];
	}
	else
	{
		for (NSInteger i = [categories count] - 1; i >= 0; --i)
		{
			[indexPaths addObject:[NSIndexPath indexPathForRow:i*2+1 inSection:0]];
		}
		
		[self.tableView deleteRowsAtIndexPaths:indexPaths withRowAnimation:UITableViewRowAnimationRight];
		[self.tableView insertRowsAtIndexPaths:[NSArray arrayWithObject:[NSIndexPath indexPathForRow:0 inSection:0]] withRowAnimation:UITableViewRowAnimationRight];
	}
	
	[indexPaths release];

	[self.tableView endUpdates];
}

- (void)deleteCategory:(CDCategory *)category indexPaths:(NSMutableArray *)indexPaths;
{
	for (CDTask *task in [category.task allObjects])
	{
		[task removeCategoriesObject:category];
		[task markDirty];
	}

	for (CDCategory *child in [category children])
		[self deleteCategory:child indexPaths:indexPaths];

	[indexPaths addObject:[NSIndexPath indexPathForRow:[categories indexOfObject:category] * 2 inSection:0]];
	[indexPaths addObject:[NSIndexPath indexPathForRow:[categories indexOfObject:category] * 2 + 1 inSection:0]];
	[category delete];

	NSError *error;
	if (![getManagedObjectContext() save:&error])
	{
		UIAlertView *alert = [[UIAlertView alloc] initWithTitle:_("Error") message:_("Could not delete category.") delegate:self cancelButtonTitle:_("OK") otherButtonTitles:nil];
		[alert show];
		[alert release];
	}
}

- (void)tableView:(UITableView *)tableView commitEditingStyle:(UITableViewCellEditingStyle)editingStyle forRowAtIndexPath:(NSIndexPath *)indexPath
{
	if (editingStyle == UITableViewCellEditingStyleDelete)
	{
		NSMutableArray *indexPaths = [[NSMutableArray alloc] init];
		[self deleteCategory:[categories objectAtIndex:indexPath.row / 2] indexPaths:indexPaths];
		[self loadCategories];
		[self.tableView deleteRowsAtIndexPaths:indexPaths withRowAnimation:UITableViewRowAnimationRight];
		[indexPaths release];
		
		if ([categories count] == 0)
			[self setEditing:NO animated:YES];
	}
	else
	{
		currentCategory = indexPath.row / 2;

		StringChoiceController *ctrl = [[StringChoiceController alloc] initWithPlaceholder:_("Enter category name") text:nil target:self action:@selector(onCategoryAdded:)];
		[self.navigationController presentModalViewController:ctrl animated:YES];
		[ctrl release];
	}
}

#pragma mark Table view methods

- (NSInteger)tableView:(UITableView *)tableView numberOfRowsInSection:(NSInteger)section
{
	if (self.editing)
	{
		return [super tableView:tableView numberOfRowsInSection:section] * 2;
	}
	else
	{
		return [super tableView:tableView numberOfRowsInSection:section] + 1;
	}
}

- (void)tableView:(UITableView *)tableView didSelectRowAtIndexPath:(NSIndexPath *)indexPath
{
	if (self.editing)
	{
		if (indexPath.row % 2)
		{
			currentCategory = indexPath.row / 2;
			
			StringChoiceController *ctrl = [[StringChoiceController alloc] initWithPlaceholder:_("Enter category name") text:nil target:self action:@selector(onCategoryAdded:)];
			[self.navigationController presentModalViewController:ctrl animated:YES];
			[ctrl release];
		}
		else
		{
			currentCategory = indexPath.row / 2;

			StringChoiceController *ctrl = [[StringChoiceController alloc] initWithPlaceholder:_("Enter category name") text:[(CDCategory *)[categories objectAtIndex:currentCategory] name] target:self action:@selector(onCategoryChanged:)];
			[self.navigationController presentModalViewController:ctrl animated:YES];
			[ctrl release];
		}
	}
	else
	{
		CDCategory *category = (indexPath.row == 0) ? nil : [categories objectAtIndex:indexPath.row - 1];
		TaskViewController *ctrl = [[CategoryTaskViewController alloc] initWithCategoryController:self edit:NO category:category];;
		[[PositionStore instance] push:self indexPath:indexPath type:TYPE_DETAILS searchWord:nil];
	
		[self.navigationController pushViewController:ctrl animated:YES];
		[ctrl release];
	}
}

- (void)onCategoryChanged:(NSString *)name
{
	if (name != nil)
	{
		CDCategory *category = [categories objectAtIndex:currentCategory];
		
		category.name = name;
		[category markDirty];

		NSError *error;
		if (![getManagedObjectContext() save:&error])
		{
			UIAlertView *alert = [[UIAlertView alloc] initWithTitle:_("Error") message:_("Could not save category.") delegate:self cancelButtonTitle:_("OK") otherButtonTitles:nil];
			[alert show];
			[alert release];
		}

		[self.tableView reloadData]; // XXXFIXME: is this necessary ?
	}

	[self.tableView deselectRowAtIndexPath:[self.tableView indexPathForSelectedRow] animated:NO];
	[self.navigationController dismissModalViewControllerAnimated:YES];
}

- (UITableViewCell *)tableView:(UITableView *)tableView cellForRowAtIndexPath:(NSIndexPath *)indexPath
{
	BadgedCell *cell;

	if (self.editing)
	{
		CDCategory *category = [categories objectAtIndex:indexPath.row / 2];
		
		if (indexPath.row % 2)
		{
			static NSString *CellIdentifier = @"BadgedCell";

			cell = (BadgedCell *)[tableView dequeueReusableCellWithIdentifier:CellIdentifier];
			if (cell == nil)
			{
				cell = [[[CellFactory cellFactory] createBadgedCell] autorelease];
			}

			cell.textLabel.text = _("Add subcategory");
			cell.textLabel.textColor = [UIColor grayColor];
			cell.badge.text = nil;
			[cell.badge clearAnnotations];

			cell.indentationLevel = [[indentations objectForKey:[category objectID]] intValue];
		}
		else
		{
			cell = (BadgedCell *)[super tableView:tableView cellForRowAtIndexPath:[NSIndexPath indexPathForRow:indexPath.row / 2 inSection:indexPath.section]];
		}
	}
	else
	{
		if (indexPath.row)
		{
			cell = (BadgedCell *)[super tableView:tableView cellForRowAtIndexPath:[NSIndexPath indexPathForRow:indexPath.row - 1 inSection:indexPath.section]];
		}
		else
		{
			static NSString *CellIdentifier = @"BadgedCell";
			
			cell = (BadgedCell *)[tableView dequeueReusableCellWithIdentifier:CellIdentifier];
			if (cell == nil)
			{
				cell = [[[CellFactory cellFactory] createBadgedCell] autorelease];
			}
			
			cell.textLabel.text = _("All");
			[cell.badge clearAnnotations];
			cell.badge.text = nil;

			cell.indentationLevel = 0;
		}

		cell.textLabel.textColor = [UIColor blackColor];
	}

	cell.accessoryType = UITableViewCellAccessoryDisclosureIndicator;
	
	[cell.badge setNeedsDisplay];
	
	[cell layoutSubviews];

	return cell;
}

- (void)onGotTotal:(NSDictionary *)dict
{
	totalCount = [[dict objectForKey:@"total"] intValue];
}

//===========================================================

- (IBAction)onSynchronize:(UIBarButtonItem *)button
{
	button.enabled = NO;

	if (![Configuration configuration].name)
	{
		// Name/domain not defined, browse
		BonjourBrowser *browser = [[BonjourBrowser alloc] initForType:@"_taskcoachsync._tcp" inDomain:@"local." customDomains:nil showDisclosureIndicators:NO showCancelButton:YES];
		browser.delegate = self;
		browser.searchingForServicesString = _("Looking for Task Coach");
		[self.navigationController presentModalViewController:browser animated:YES];
		[browser release];
	}
	else
	{
		NSNetService *srv = [[NSNetService alloc] initWithDomain:[Configuration configuration].domain type:@"_taskcoachsync._tcp" name:[Configuration configuration].name];
		srv.delegate = self;
		[srv resolveWithTimeout:5];
	}
}

- (UITableViewCellEditingStyle)tableView:(UITableView *)tableView editingStyleForRowAtIndexPath:(NSIndexPath *)indexPath
{
	return (indexPath.row % 2) ? UITableViewCellEditingStyleInsert : UITableViewCellEditingStyleDelete;
}

#pragma mark NSNetService methods

- (void)netService:(NSNetService *)sender didNotResolve:(NSDictionary *)errorDict
{
	// Browse again...

	BonjourBrowser *browser = [[BonjourBrowser alloc] initForType:@"_taskcoachsync._tcp" inDomain:@"local." customDomains:nil showDisclosureIndicators:NO showCancelButton:YES];
	browser.delegate = self;
	browser.searchingForServicesString = _("Looking for Task Coach");
	[self.navigationController presentModalViewController:browser animated:YES];
	[browser release];
	[sender release];
}

- (void)netServiceDidResolveAddress:(NSNetService *)sender
{
	SyncViewController *ctrl = [[SyncViewController alloc] initWithTarget:self action:@selector(onSyncFinished) host:[sender hostName] port:[sender port]];
	[self.navigationController presentModalViewController:ctrl animated:YES];
	[ctrl release];
}

- (void)onSyncFinished
{
	[self loadCategories];
	[self.tableView reloadData];
	[self.navigationController dismissModalViewControllerAnimated:YES];
	syncButton.enabled = YES;
	fileButton.enabled = [Configuration configuration].cdFileCount >= 2;
}

- (void)bonjourBrowser:(BonjourBrowser*)browser didResolveInstance:(NSNetService*)ref
{
	if (ref)
	{
		NSLog(@"Found Task Coach: %@:%d", [ref hostName], [ref port]);

		[Configuration configuration].domain = [ref domain];
		[Configuration configuration].name = [ref name];
		[[Configuration configuration] save];

		SyncViewController *ctrl = [[SyncViewController alloc] initWithTarget:self action:@selector(onSyncFinished) host:[ref hostName] port:[ref port]];
		[self.navigationController.modalViewController presentModalViewController:ctrl animated:YES];
		[ctrl release];
	}
	else
	{
		syncButton.enabled = YES;
		[self.navigationController dismissModalViewControllerAnimated:YES];
	}
}

@end

