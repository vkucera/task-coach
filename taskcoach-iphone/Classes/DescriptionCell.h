//
//  DescriptionCell.h
//  TaskCoach
//
//  Created by Jérôme Laheurte on 07/02/09.
//  Copyright 2009 Jérôme Laheurte. See COPYING for details.
//

#import <UIKit/UIKit.h>

@interface DescriptionCell : UITableViewCell
{
	UITextView *textView;
}

@property (nonatomic, retain) IBOutlet UITextView *textView;

@end
