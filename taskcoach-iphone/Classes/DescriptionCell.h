//
//  DescriptionCell.h
//  TaskCoach
//
//  Created by Jérôme Laheurte on 07/02/09.
//  Copyright 2009 __MyCompanyName__. All rights reserved.
//

#import <UIKit/UIKit.h>

@interface DescriptionCell : UITableViewCell
{
	UITextView *textView;
}

@property (nonatomic, retain) IBOutlet UITextView *textView;

@end
