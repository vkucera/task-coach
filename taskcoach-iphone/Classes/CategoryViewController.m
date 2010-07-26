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
#import "StringChoiceAlert.h"
#import "CategoryTaskViewController.h"
#import "ParentTaskViewController.h"
#import "NewCategoryiPad.h"
#import "SyncViewController.h"
#import "FileChooser.h"
#import "BadgedCell.h"
#import "CellFactory.h"
#import "NSDate+Utils.h"
#import "ReminderController.h"
#import "LogUtils.h"

#import "CDDomainObject+Addons.h"
#import "CDCategory.h"
#import "CDTask.h"
#import "CDTask+Addons.h"
#import "CDHierarchicalDomainObject+Addons.h"

#import "Configuration.h"
#import "i18n.h"

@implementation CategoryViewController

@synthesize navigationController;
@synthesize splitCtrl;
@synthesize syncButton;
@synthesize fileButton;
@synthesize taskCtrl;
@synthesize theToolbar;

- (void)loadCategories
{
	[super loadCategories];
	
	[self editButtonItem].enabled = ([categories count] != 0);
	fileButton.enabled = ([Configuration configuration].cdFileCount >= 2);
}

- (void)willTerminate
{
	[[PositionStore instance] push:self indexPath:nil type:0 searchWord:nil];
}

- (void)restorePosition:(Position *)pos store:(PositionStore *)store
{
	[self.tableView setContentOffset:pos.scrollPosition animated:NO];

	if ((pos.indexPath.section >= [self numberOfSectionsInTableView:self.tableView]) ||
		(pos.indexPath.row >= [self tableView:self.tableView numberOfRowsInSection:pos.indexPath.section]))
		return;

	if (pos.indexPath)
	{
		[self.tableView selectRowAtIndexPath:pos.indexPath animated:NO scrollPosition:UITableViewScrollPositionNone];

		CDCategory *category = nil;

		if (pos.indexPath.row)
		{
			category = [categories objectAtIndex:pos.indexPath.row - 1];
		}

		if (UI_USER_INTERFACE_IDIOM() == UIUserInterfaceIdiomPhone)
		{
			[[PositionStore instance] push:self indexPath:pos.indexPath type:pos.type searchWord:nil];

			CategoryTaskViewController *ctrl = [[CategoryTaskViewController alloc] initWithCategoryController:self edit:self.editing category:category];
			[self.navigationController pushViewController:ctrl animated:YES];
			[ctrl release];
			
			[store restore:ctrl];
		}
		else
		{
			[[PositionStore instance] setRoot:self indexPath:pos.indexPath type:pos.type searchWord:nil];

			[taskCtrl setCategory:category];
			[store restore:taskCtrl];
		}
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

	if (UI_USER_INTERFACE_IDIOM() == UIUserInterfaceIdiomPad)
	{
		NSMutableArray *items = [[NSMutableArray alloc] init];
		[items addObjectsFromArray:self.theToolbar.items];
		[items addObject:[self editButtonItem]];
		[self.theToolbar setItems:items animated:NO];
		[items release];
	}
}

- (void)viewDidUnload
{
	self.navigationController = nil;
	self.splitCtrl = nil;
	self.theToolbar = nil;

	self.syncButton = nil;
	
	[categories release];
	categories = nil;
	
	[indentations release];
	indentations = nil;
}

- (void)dealloc
{
	[self viewDidUnload];
	
	[super dealloc];
}

- (void)didRotateFromInterfaceOrientation:(UIInterfaceOrientation)fromInterfaceOrientation
{
	if (popoverCtrl)
	{
		[popoverCtrl dismissPopoverAnimated:NO];
		[popoverCtrl release];
		popoverCtrl = nil;
	}
}

- (void)viewDidAppear:(BOOL)animated
{
	[super viewDidAppear:animated];

	NSDate *nextUpdate = [NSDate dateRounded];
	nextUpdate = [nextUpdate addTimeInterval:61];
	minuteTimer = [[NSTimer alloc] initWithFireDate:nextUpdate interval:60 target:self selector:@selector(onMinuteTimer:) userInfo:nil repeats:YES];
	[[NSRunLoop currentRunLoop] addTimer:minuteTimer forMode:NSDefaultRunLoopMode];
}

- (void)viewWillDisappear:(BOOL)animated
{
	[minuteTimer invalidate];
	[minuteTimer release];
	minuteTimer = nil;
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
	if (UI_USER_INTERFACE_IDIOM() == UIUserInterfaceIdiomPad)
	{
		[taskCtrl setCategory:nil];
		[self onSynchronize:syncButton];
	}
	else
		wantSync = YES;
}

- (IBAction)onChooseFile:(UIBarButtonItem *)button
{
	FileChooser *chooser = [[FileChooser alloc] initWithController:self];

	if (UI_USER_INTERFACE_IDIOM() == UIUserInterfaceIdiomPad)
	{
		chooser.modalPresentationStyle = UIModalPresentationFormSheet;
		[splitCtrl presentModalViewController:chooser animated:YES];
	}
	else
	{
		[self.navigationController presentModalViewController:chooser animated:YES];
	}

	[chooser release];
}

- (IBAction)onAddCategory:(UIBarButtonItem *)button
{
	currentCategory = -1;
	if (UI_USER_INTERFACE_IDIOM() == UIUserInterfaceIdiomPhone)
	{
		StringChoiceAlert *alert = [[StringChoiceAlert alloc] initWithPlaceholder:_("Enter category name") text:nil target:self action:@selector(onCategoryAdded:)];
		alert.textField.autocapitalizationType = UITextAutocapitalizationTypeSentences;
		[alert show];
		[alert release];
	}
	else
	{
		NewCategoryiPad *ctrl = [[NewCategoryiPad alloc] initWithString:nil target:self action:@selector(onCategoryAdded:)];
		popoverCtrl = [[UIPopoverController alloc] initWithContentViewController:ctrl];
		[ctrl release];
		popoverCtrl.delegate = self;
		[popoverCtrl setPopoverContentSize:CGSizeMake(259, 116)];
		[popoverCtrl presentPopoverFromBarButtonItem:button permittedArrowDirections:UIPopoverArrowDirectionAny animated:YES];
	}
}

- (void)popoverControllerDidDismissPopover:(UIPopoverController *)popoverController
{
	[popoverCtrl release];
	popoverCtrl = nil;
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
		[newCat save];

		[self loadCategories];
		[self.tableView reloadData];
	}

	if (UI_USER_INTERFACE_IDIOM() == UIUserInterfaceIdiomPhone)
	{
		[self.navigationController dismissModalViewControllerAnimated:YES];
	}
	else
	{
		[popoverCtrl dismissPopoverAnimated:YES];
		[popoverCtrl release];
		popoverCtrl = nil;
	}

	[self.tableView deselectRowAtIndexPath:[self.tableView indexPathForSelectedRow] animated:NO];
}

- (void)fillCell:(BadgedCell *)cell forCategory:(CDCategory *)category
{
	[super fillCell:cell forCategory:category];

	cell.textLabel.text = [category name];

	NSInteger total = 0, overdue = 0, dueSoon = 0, started = 0;

	NSFetchRequest *request = [[NSFetchRequest alloc] init];
	[request setEntity:[NSEntityDescription entityForName:@"CDTask" inManagedObjectContext:getManagedObjectContext()]];

	NSMutableArray *preds = [[NSMutableArray alloc] initWithCapacity:3];
	[preds addObject:[NSPredicate predicateWithFormat:@"status != %d AND ANY categories IN %@ AND parent == NULL", STATUS_DELETED, [category selfAndChildren]]];
	if (![Configuration configuration].showCompleted)
		[preds addObject:[NSPredicate predicateWithFormat:@"dateStatus != %d", TASKSTATUS_COMPLETED]];
	if (![Configuration configuration].showInactive)
		[preds addObject:[NSPredicate predicateWithFormat:@"dateStatus != %d", TASKSTATUS_NOTSTARTED]];
	[request setPredicate:[NSCompoundPredicate andPredicateWithSubpredicates:preds]];
	[preds release];

	NSError *error;
	NSArray *tasks = [getManagedObjectContext() executeFetchRequest:request error:&error];
	[request release];

	if (tasks)
	{
		for (CDTask *task in tasks)
		{
			++total;

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
		JLERROR("Could not fetch tasks: %s", [[error localizedDescription] UTF8String]);
	}

	cell.badge.text = [NSString stringWithFormat:@"%d", total];
	cell.badge.capsuleColor = [UIColor blackColor];
	
	[cell.badge addAnnotation:[NSString stringWithFormat:@"%d", dueSoon] capsuleColor:[UIColor orangeColor]];
	[cell.badge addAnnotation:[NSString stringWithFormat:@"%d", overdue] capsuleColor:[UIColor redColor]];
	[cell.badge addAnnotation:[NSString stringWithFormat:@"%d", started] capsuleColor:[UIColor blueColor]];
	
	[cell resize];
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
	[category save];
}

- (void)tableView:(UITableView *)tableView commitEditingStyle:(UITableViewCellEditingStyle)editingStyle forRowAtIndexPath:(NSIndexPath *)indexPath
{
	if (editingStyle == UITableViewCellEditingStyleDelete)
	{
		if ([taskCtrl compareCategory:[categories objectAtIndex:indexPath.row / 2]])
		{
			[taskCtrl.navigationController popToRootViewControllerAnimated:YES];
			[taskCtrl setCategory:nil];
			[[PositionStore instance] setRoot:self indexPath:[NSIndexPath indexPathForRow:0 inSection:0] type:TYPE_DETAILS searchWord:nil];
		}

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

		StringChoiceAlert *alert = [[StringChoiceAlert alloc] initWithPlaceholder:_("Enter category name") text:nil target:self action:@selector(onCategoryAdded:)];
		alert.textField.autocapitalizationType = UITextAutocapitalizationTypeSentences;
		[alert show];
		[alert release];
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
	if (taskCtrl.popCtrl)
	{
		[taskCtrl.popCtrl dismissPopoverAnimated:YES];
	}

	if (self.editing)
	{
		if (indexPath.row % 2)
		{
			currentCategory = indexPath.row / 2;
			
			if (UI_USER_INTERFACE_IDIOM() == UIUserInterfaceIdiomPhone)
			{
				StringChoiceAlert *alert = [[StringChoiceAlert alloc] initWithPlaceholder:_("Enter category name") text:nil target:self action:@selector(onCategoryAdded:)];
				alert.textField.autocapitalizationType = UITextAutocapitalizationTypeSentences;
				[alert show];
				[alert release];
			}
			else
			{
				NewCategoryiPad *ctrl = [[NewCategoryiPad alloc] initWithString:nil target:self action:@selector(onCategoryAdded:)];
				popoverCtrl = [[UIPopoverController alloc] initWithContentViewController:ctrl];
				[ctrl release];
				popoverCtrl.delegate = self;
				[popoverCtrl setPopoverContentSize:CGSizeMake(259, 116)];
				[popoverCtrl presentPopoverFromRect:[self.tableView cellForRowAtIndexPath:indexPath].frame inView:self.view permittedArrowDirections:UIPopoverArrowDirectionAny animated:YES];
			}
		}
		else
		{
			currentCategory = indexPath.row / 2;

			if (UI_USER_INTERFACE_IDIOM() == UIUserInterfaceIdiomPhone)
			{
				StringChoiceAlert *alert = [[StringChoiceAlert alloc] initWithPlaceholder:_("Enter category name") text:[(CDCategory *)[categories objectAtIndex:currentCategory] name] target:self action:@selector(onCategoryChanged:)];
				alert.textField.autocapitalizationType = UITextAutocapitalizationTypeSentences;
				[alert show];
				[alert release];
			}
			else
			{
				NewCategoryiPad *ctrl = [[NewCategoryiPad alloc] initWithString:[(CDCategory *)[categories objectAtIndex:currentCategory] name] target:self action:@selector(onCategoryChanged:)];
				popoverCtrl = [[UIPopoverController alloc] initWithContentViewController:ctrl];
				[ctrl release];
				popoverCtrl.delegate = self;
				[popoverCtrl setPopoverContentSize:CGSizeMake(259, 116)];
				[popoverCtrl presentPopoverFromRect:[self.tableView cellForRowAtIndexPath:indexPath].frame inView:self.view permittedArrowDirections:UIPopoverArrowDirectionAny animated:YES];
			}
		}
	}
	else
	{
		CDCategory *category = (indexPath.row == 0) ? nil : [categories objectAtIndex:indexPath.row - 1];

		if (UI_USER_INTERFACE_IDIOM() == UIUserInterfaceIdiomPhone)
		{
			TaskViewController *ctrl = [[CategoryTaskViewController alloc] initWithCategoryController:self edit:NO category:category];;
	
			[self.navigationController pushViewController:ctrl animated:YES];
			[ctrl release];

			[[PositionStore instance] push:self indexPath:indexPath type:TYPE_DETAILS searchWord:nil];
		}
		else
		{
			[self.tableView deselectRowAtIndexPath:indexPath animated:YES];
			[taskCtrl setCategory:category];
			[taskCtrl.calendarView reloadDay];

			[[PositionStore instance] setRoot:self indexPath:indexPath type:TYPE_DETAILS searchWord:nil];
		}
	}
}

- (void)selectAll
{
	[taskCtrl setCategory:nil];
	[taskCtrl.calendarView reloadDay];
}

- (void)onCategoryChanged:(NSString *)name
{
	if (name != nil)
	{
		CDCategory *category = [categories objectAtIndex:currentCategory];
		
		category.name = name;
		[category markDirty];
		[category save];

		[self.tableView reloadData];
	}

	[self.tableView deselectRowAtIndexPath:[self.tableView indexPathForSelectedRow] animated:NO];

	if (UI_USER_INTERFACE_IDIOM() == UIUserInterfaceIdiomPhone)
	{
		[self.navigationController dismissModalViewControllerAnimated:YES];
	}
	else
	{
		[popoverCtrl dismissPopoverAnimated:YES];
		[popoverCtrl release];
		popoverCtrl = nil;
	}
}

- (UITableViewCell *)tableView:(UITableView *)tableView cellForRowAtIndexPath:(NSIndexPath *)indexPath
{
	BadgedCell *cell = nil;

	if (self.editing)
	{
		CDCategory *category = [categories objectAtIndex:indexPath.row / 2];
		
		if (indexPath.row % 2)
		{
			static NSString *CellIdentifier = @"BadgedCell";

			if (UI_USER_INTERFACE_IDIOM() == UIUserInterfaceIdiomPhone)
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
			
			if (UI_USER_INTERFACE_IDIOM() == UIUserInterfaceIdiomPhone)
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

	if (UI_USER_INTERFACE_IDIOM() == UIUserInterfaceIdiomPhone)
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

	// Always browse; there may be several Task Coach instances on the network
	BonjourBrowser *browser = [[BonjourBrowser alloc] initForType:@"_taskcoachsync._tcp" inDomain:@"local." customDomains:nil showDisclosureIndicators:NO showCancelButton:YES];
	browser.delegate = self;
	browser.searchingForServicesString = _("Looking for Task Coach");
	
	if (UI_USER_INTERFACE_IDIOM() == UIUserInterfaceIdiomPad)
	{
		browser.modalPresentationStyle = UIModalPresentationFormSheet;
		[splitCtrl presentModalViewController:browser animated:YES];
	}
	else
	{
		[self.navigationController presentModalViewController:browser animated:YES];
	}
	
	[browser release];
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

	if (UI_USER_INTERFACE_IDIOM() == UIUserInterfaceIdiomPad)
	{
		browser.modalPresentationStyle = UIModalPresentationFormSheet;
		[splitCtrl presentModalViewController:browser animated:YES];
	}
	else
	{
		[self.navigationController presentModalViewController:browser animated:YES];
	}

	[browser release];
	[sender release];
}

- (void)netServiceDidResolveAddress:(NSNetService *)sender
{
	SyncViewController *ctrl = [[SyncViewController alloc] initWithTarget:self action:@selector(onSyncFinished) host:[sender hostName] port:[sender port] name:[sender name]];

	NSLog(@"Service name: %@", [sender name]);

	if (UI_USER_INTERFACE_IDIOM() == UIUserInterfaceIdiomPad)
	{
		ctrl.modalPresentationStyle = UIModalPresentationFormSheet;
		[splitCtrl presentModalViewController:ctrl animated:YES];
	}
	else
	{
		[self.navigationController presentModalViewController:ctrl animated:YES];
	}

	[ctrl release];
}

- (void)onSyncFinished
{
	[self loadCategories];
	[self.tableView reloadData];

	if (UI_USER_INTERFACE_IDIOM() == UIUserInterfaceIdiomPhone)
	{
		[self.navigationController dismissModalViewControllerAnimated:YES];
	}
	else
	{
		[self selectAll];

		[splitCtrl dismissModalViewControllerAnimated:YES];
	}

	syncButton.enabled = YES;
}

- (void)bonjourBrowser:(BonjourBrowser*)browser didResolveInstance:(NSNetService*)ref
{
	if (ref)
	{
		NSLog(@"Found Task Coach: %@:%d", [ref hostName], [ref port]);

		[Configuration configuration].domain = [ref domain];
		[Configuration configuration].name = [ref name];
		[[Configuration configuration] save];

		SyncViewController *ctrl = [[SyncViewController alloc] initWithTarget:self action:@selector(onSyncFinished) host:[ref hostName] port:[ref port] name:[ref name]];

		NSLog(@"Service name: %@", [ref name]);

		if (UI_USER_INTERFACE_IDIOM() == UIUserInterfaceIdiomPad)
		{
			ctrl.modalPresentationStyle = UIModalPresentationFormSheet;
			[browser presentModalViewController:ctrl animated:YES];
		}
		else
		{
			[self.navigationController.modalViewController presentModalViewController:ctrl animated:YES];
		}

		[ctrl release];
	}
	else
	{
		syncButton.enabled = YES;
		
		if (UI_USER_INTERFACE_IDIOM() == UIUserInterfaceIdiomPhone)
			[self.navigationController dismissModalViewControllerAnimated:YES];
		else
			[splitCtrl dismissModalViewControllerAnimated:YES];
	}
}

@end

